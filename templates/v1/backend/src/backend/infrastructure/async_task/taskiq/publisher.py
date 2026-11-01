"""任务投递器：按任务名直投 Taskiq Broker，附加保留参数 outbox_id。"""

from typing import Protocol

from taskiq import AsyncBroker
from taskiq.kicker import AsyncKicker

from backend.infrastructure.async_task.taskiq.broker import get_broker


class TaskPublisher(Protocol):
    async def publish(self, task_name: str, payload: dict, *, outbox_id: int) -> None: ...


class TaskiqPublisher:
    """AsyncKicker 按任务名解析注册任务并直投，无需持有函数引用。"""

    def __init__(self, broker: AsyncBroker | None = None):
        self._broker = broker

    @property
    def broker(self) -> AsyncBroker:
        return self._broker if self._broker is not None else get_broker()

    async def publish(self, task_name: str, payload: dict, *, outbox_id: int) -> None:
        kicker = AsyncKicker(task_name, self.broker, labels={})
        await kicker.kiq(payload=payload, outbox_id=outbox_id)
