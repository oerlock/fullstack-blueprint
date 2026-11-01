"""Worker 运行入口：

    uv run taskiq worker backend.worker.run:broker --workers 4
"""

import backend.worker.tasks  # noqa: F401  任务注册
from backend.infrastructure.async_task.taskiq.broker import get_broker

broker = get_broker()
