"""投递周期任务：由 Taskiq Scheduler 按配置周期触发。"""

from backend.config.settings import settings
from backend.infrastructure.async_task.relay.service import TaskRelayService
from backend.infrastructure.async_task.session import get_task_session_factory
from backend.infrastructure.async_task.taskiq.broker import get_broker
from backend.infrastructure.async_task.taskiq.publisher import TaskiqPublisher

broker = get_broker()


@broker.task(
    task_name="dispatch_outbox_tasks",
    schedule=[{"interval": settings.tasks.relay.poll_interval_seconds}],
)
async def dispatch_outbox_tasks() -> int:
    service = TaskRelayService(
        get_task_session_factory(),
        TaskiqPublisher(get_broker()),
        relay_settings=settings.tasks.relay,
    )
    return await service.dispatch_tick()
