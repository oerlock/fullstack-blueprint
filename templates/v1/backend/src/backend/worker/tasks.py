"""统一注册业务任务模块。只负责导入完成任务注册，不承载业务逻辑。"""

import importlib

# 新增业务任务后在此登记，例如 "backend.apps.report.tasks.generate_report"
TASK_MODULES = [
    "backend.infrastructure.async_task.taskiq.dispatch_task",
]

for _module_name in TASK_MODULES:
    importlib.import_module(_module_name)
