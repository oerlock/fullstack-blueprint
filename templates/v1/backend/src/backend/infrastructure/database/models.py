"""业务模型统一注册，供 Alembic 识别。

新增业务模块的数据库模型后，在此导入，否则自动生成迁移时会遗漏相关表。
本模块只负责导入模型，不应触发业务初始化或其他运行时副作用。
"""

# from backend.apps.account.models import User

from backend.infrastructure.async_task.execution.models import TaskExecution  # noqa: F401
from backend.infrastructure.async_task.outbox.models import TaskOutbox  # noqa: F401
