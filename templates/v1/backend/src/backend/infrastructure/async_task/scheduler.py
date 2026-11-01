"""Taskiq Scheduler 入口：

    uv run taskiq scheduler backend.infrastructure.async_task.scheduler:scheduler
"""

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from backend.infrastructure.async_task.taskiq.broker import get_broker


def build_scheduler() -> TaskiqScheduler:
    broker = get_broker()
    # 导入业务任务模块以完成注册（含 dispatch_task 的周期标签）
    import backend.worker.tasks  # noqa: F401  pylint: disable=unused-import

    return TaskiqScheduler(broker, sources=[LabelScheduleSource(broker)])


scheduler = build_scheduler()
