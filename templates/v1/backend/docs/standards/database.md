# 数据库规范

## OceanBase

项目使用 OceanBase MySQL 模式，使用 SQLModel 定义数据模型，使用 SQLAlchemy 提供数据库访问能力，使用 Alembic 管理数据库结构迁移。

### 时间字段

- 时间字段统一使用 `DATETIME(6)`，由应用层统一采用 UTC 时间。
- 创建时间 `created_at` 默认使用 `CURRENT_TIMESTAMP(6)`。
- 更新时间 `updated_at` 必须在数据更新时维护，统一采用数据库触发器实现。
- 需要统一事务内的时间时，由应用层获取一次并复用，不依赖数据库时间函数的事务语义。

### ID 字段

- **对外业务实体表**：使用 UUIDv7 作为主键，由应用层生成。
  - 数据库使用 `BINARY(16)` 存储 UUID。
  - Python 层统一使用 `uuid.UUID`。
  - 通过 SQLAlchemy 自定义类型统一处理 UUID 与二进制数据之间的转换。
- **内部系统表**：使用 `BIGINT AUTO_INCREMENT` 作为主键。
- UUIDv7 由应用层生成，不依赖数据库生成 UUID。

### 表结构与约束

- 表名、字段名统一使用小写 `snake_case`。
- 表名统一使用复数形式，例如 `account_users`、`agent_threads`。
- 外键字段采用 `<referenced_singular>_id` 命名，例如 `user_id`、`role_id`。
- 所有表必须显式定义主键。
- 唯一性要求通过数据库唯一约束保证，不以应用层检查代替数据库约束。
- 外键根据实际的数据一致性要求显式定义。
- 索引根据查询条件、排序方式、关联关系和唯一性要求设计，避免重复创建等价索引。
- 软删除统一使用 `deleted_at` 字段，未删除时为 `NULL`。

### 约束命名规范

| 类型 | 命名规范 | 示例 |
|---|---|---|
| 主键 | `pk_<table>` | `pk_account_user_roles` |
| 外键 | `fk_<table>_<referenced>` | `fk_account_user_roles_role` |
| 唯一约束 | `uk_<table>_<columns>` | `uk_account_roles_code` |
| 检查约束 | `chk_<table>_<rule>` | `chk_account_roles_code_format` |
| 索引 | `idx_<table>_<columns>` | `idx_account_user_roles_role_user` |
| 触发器 | `trg_<table>_<action>` | `trg_account_users_updated_at` |

约束与索引的命名必须在模型定义、Alembic 迁移脚本和实际数据库结构之间保持一致。

### SQLModel 与 SQLAlchemy

- 使用 SQLModel 定义数据库表模型，不重复维护同一张表的 ORM 模型。
- 使用 SQLAlchemy 的列参数、约束和索引配置表达数据库结构。
- 数据库默认值、自动更新时间和数据库专属功能必须明确配置，不假设 SQLModel 会自动实现。
- UUIDv7 的生成逻辑由应用层负责，UUID 的二进制转换统一由 SQLAlchemy 自定义类型处理。
- 对 ORM 无法清晰表达的数据库特性，通过 Alembic 迁移脚本实现。
- 不依赖 `SQLModel.metadata.create_all()` 作为生产环境的数据库结构管理机制。

### Alembic 迁移规范

- 所有数据库结构变更必须通过 Alembic 迁移管理。
- Alembic 迁移脚本必须纳入版本控制。
- 新增或修改 SQLModel 表模型后，使用 Alembic 自动生成迁移脚本，并在提交前检查和修正生成结果。
- 自动生成的迁移脚本不得未经检查直接用于生产环境。
- 迁移脚本必须覆盖实际模型变更，包括表、字段、索引、约束及其他数据库对象。
- 迁移脚本中的对象命名必须遵守本规范。
- 数据库触发器等无法通过模型自动检测的对象，由迁移脚本显式创建、修改和删除。
- 迁移脚本必须考虑已有数据、数据兼容性、执行顺序和回滚方案。
- 生产环境通过 Alembic 执行迁移，禁止直接手动修改数据库结构。
- 紧急情况下进行数据库变更后，必须补充对应的迁移脚本，确保迁移历史与实际数据库结构一致。
- 不得随意修改已经在共享环境执行过的迁移脚本；需要调整时，应新增迁移版本。

### 数据库专属功能

- 使用 OceanBase MySQL 模式支持的 SQL 语法、数据类型和数据库对象。
- 自增主键使用 `BIGINT AUTO_INCREMENT`。
- UUID 使用 `BINARY(16)` 存储。
- `updated_at` 通过 `BEFORE UPDATE` 触发器维护。
- 当前时间使用 `CURRENT_TIMESTAMP(6)`，需要统一事务内时间时由应用层处理。
- 使用检查约束、外键、触发器等功能前，应确认目标 OceanBase 版本及 MySQL 模式对相应功能的支持情况。
- Alembic 自动生成的迁移脚本必须针对 OceanBase 的兼容性进行验证。

### 触发器示例

更新时间触发器由 Alembic 迁移脚本创建：

```sql
CREATE TRIGGER trg_account_users_updated_at
BEFORE UPDATE ON account_users
FOR EACH ROW
SET NEW.updated_at = CURRENT_TIMESTAMP(6);
```

对应的时间字段定义示例：

```sql
created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
```

### 执行原则

- **SQLModel**：维护数据模型定义。
- **SQLAlchemy**：提供数据库访问、类型映射和 ORM 支持。
- **Alembic**：维护数据库结构的版本历史并执行迁移。
- **OceanBase**：负责持久化及数据库约束的最终执行。
- **应用层**：负责 UUIDv7 生成、业务规则和统一时间处理。

数据库模型、迁移历史和实际数据库结构必须保持一致。