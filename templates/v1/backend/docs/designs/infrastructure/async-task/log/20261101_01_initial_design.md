# 20261101-01 初版设计

- 确定方案：Transactional Outbox + Taskiq（Redis Stream Broker）。
- 关键决策：
  - MySQL 8 / OceanBase 适配：`JSON` 列、部分索引改为普通复合索引、CHECK 约束由应用层保证、`updated_at` 用 MySQL 原生 `ON UPDATE`。
  - 投递由 Taskiq Scheduler 周期触发，不设独立 Dispatcher 进程 / CLI。
  - 任务注册遵循 `docs/standards/project_structure.md` 第十章：`worker/run.py` + `worker/tasks.py`，业务任务放 `apps/<app>/tasks/`。
