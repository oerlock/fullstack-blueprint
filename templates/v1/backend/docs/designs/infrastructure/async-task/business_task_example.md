# 业务任务示例

以 `generate_report` 为例，三步接入一个业务任务。

## 1. 定义任务 DTO 与任务函数（`src/backend/apps/<app>/tasks/report.py`）

任务参数用 pydantic DTO 描述：创建任务时 `model_dump(mode='json')`，执行时 `model_validate` 还原，序列化类型由 DTO 收敛。

```python
from pydantic import BaseModel

from backend.infrastructure.async_task.taskiq.broker import get_broker
from backend.infrastructure.async_task.taskiq.execution import task_execution

# 必须使用共享单例：任务注册只作用于装饰时的 broker 实例
broker = get_broker()


class GenerateReportDTO(BaseModel):
    report_id: str


@broker.task(task_name="generate_report")
@task_execution
async def generate_report(*, payload: dict):
    dto = GenerateReportDTO.model_validate(payload)
    # 任务内自行管理 Session
    ...
```

## 2. 注册到 Worker（`src/backend/worker/tasks.py`）

```python
TASK_MODULES = [
    "backend.apps.<app>.tasks.report",
]
```

## 3. 业务事务中创建任务

```python
async with session.begin():
    report = Report(...)
    session.add(report)
    outbox = await TaskOutboxService(session).create(
        CreateTaskOutboxDTO(
            task_name="generate_report",
            business_id=str(report.id),
            user_id=user_id,
            payload=GenerateReportDTO(report_id=str(report.id)).model_dump(mode="json"),
        )
    )
```

## 运行

```bash
uv run taskiq worker backend.worker.run:broker --workers 4
uv run taskiq scheduler backend.infrastructure.async_task.scheduler:scheduler
```

## 约定

- `payload` 整体作为单个 dict 参数传给任务函数；`outbox_id` 为投递侧保留参数，payload 中不允许同名键。
- 需要执行失败重试的任务，装饰时加 `retry_on_error=True`，可用 `max_retries` 标签覆盖默认 `TASKS__MAX_RETRY_COUNT`。
- 任务必须幂等（At-Least-Once 语义下可能重复执行）。
- 任务内自行管理数据库 Session 生命周期。
