# FastAPI 后端项目目录结构规范

## 一、设计目标

采用轻量模块化单体（Modular Monolith）架构，按业务域组织代码，通过明确的模块职责和依赖规则控制复杂度。

核心原则：

1. **按业务域组织**：业务代码围绕业务模块划分，而不是围绕技术类型划分。
2. **职责明确**：业务逻辑、基础设施、接口装配和运行入口相互分离。
3. **边界清晰**：不同业务模块通过公开 Service 接口交互，不直接访问彼此的内部实现。
4. **技术解耦**：目录命名尽量采用通用职责名称，具体技术选型由内部实现决定。
5. **渐进式拆分**：初期保持简单，只有职责复杂度确实增加时才拆分目录和模块。
6. **避免过度设计**：不强制引入完整 DDD、Repository 或额外抽象层。

## 二、完整目录结构

```text
backend/
├── .env.d/                             # 本地环境变量（Git Ignore）
├── .support/                           # 本地运行支持文件（Git Ignore）
├── .example.env.d/                     # 环境变量示例
├── .example.support/                   # 运行支持文件示例（按需）
│
├── devops/                             # 部署与运维脚本
├── docs/                               # 项目文档
├── requirements/                       # 依赖快照（按需）
│
├── migrations/                         # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── src/
│   └── backend/
│       ├── __init__.py
│       ├── main.py                     # 应用入口
│       │
│       ├── apps/                       # 业务模块
│       │   ├── account/
│       │   ├── ticket/
│       │   └── notification/
│       │
│       ├── config/                     # 配置管理
│       ├── core/                       # 通用基础能力
│       ├── infrastructure/             # 基础设施
│       ├── errors/                     # 全局异常与错误码
│       ├── presentation/                # 接口层装配
│       ├── cli/                        # 命令行入口
│       ├── worker/                     # 后台任务运行入口
│       └── scripts/                    # 全局运行时维护脚本
│
├── tests/                              # 自动化测试
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── factories/
│   └── conftest.py
│
├── .coveragerc
├── .gitignore
├── alembic.ini
├── manage.py                           # 命令行统一入口
├── pyproject.toml
├── pytest.ini
├── README.md
└── uv.lock
```

说明：

- `.env.d/`：存放本地环境配置，通常不提交 Git。
- `.support/`：存放本地运行所需的辅助文件，例如本地证书、数据文件等。
- `.example.env.d/`：环境配置示例，供开发者初始化环境。
- `.example.support/`：运行支持文件示例，按需提供。
- `devops/`：存放部署、CI/CD、环境初始化等运维辅助脚本。
- `docs/`：存放项目架构、开发规范、接口说明等文档。
- `requirements/`：按需存放依赖快照或不同环境的依赖清单。
- `migrations/`：统一管理数据库迁移文件。
- `src/backend/`：应用程序主体代码。
- `tests/`：自动化测试代码。

## 三、业务模块 apps

### 3.1 目录结构

按业务域划分，每个业务模块使用单数命名。

例如：

- `account`：账户管理
- `ticket`：工单管理
- `notification`：通知管理

初始结构：

```text
apps/
├── account/
│   ├── __init__.py
│   ├── routes.py                       # 业务路由
│   ├── schemas.py                      # 请求与响应结构
│   ├── models.py                       # 数据模型
│   ├── services.py                     # 业务逻辑与用例编排
│   ├── deps.py                         # 业务依赖装配（按需）
│   ├── config.py                       # 业务模块配置（按需）
│   ├── errors.py                       # 业务异常（按需）
│   ├── domain/                         # 领域规则（按需）
│   ├── repositories/                   # 数据访问（按需）
│   ├── tasks/                          # 异步任务（按需）
│   ├── admin/                          # 管理端能力（按需）
│   └── scripts/                        # 业务维护脚本（按需）
│
├── ticket/
│   └── ...
│
└── notification/
    └── ...
```

以上是一个业务模块可能使用的完整结构，实际开发中不需要一次性创建所有目录和文件。

### 3.2 文件职责

| 文件或目录 | 职责 |
|---|---|
| `routes.py` | 定义业务 HTTP 路由及请求响应编排 |
| `deps.py` | 定义业务模块专属的依赖注入 |
| `config.py` | 定义业务模块专属配置，由全局配置（`config/settings.py`）聚合 |
| `schemas.py` | 定义请求参数、响应数据及校验结构 |
| `models.py` | 定义数据库模型 |
| `services.py` | 实现业务用例、业务流程及公开服务接口 |
| `errors.py` | 定义业务模块专属异常 |
| `domain/` | 存放领域实体、值对象及领域规则 |
| `repositories/` | 封装数据访问与复杂查询 |
| `tasks/` | 定义业务模块专属的异步任务 |
| `admin/` | 管理端相关能力 |
| `scripts/` | 业务模块专属的数据维护与处理脚本 |

### 3.3 跨业务模块依赖约定

每个 app 通过 `services.py` 提供对其他 app 公开的业务服务接口。

约定：

1. `services.py` 中的公开函数允许其他 app 调用。
2. `repositories/`、`domain/`、`models.py` 等属于 app 内部实现，不允许跨 app 直接导入。
3. 跨 app 交互只依赖对方公开的 Service 接口。
4. 公开接口应保持稳定，内部实现可以独立调整。
5. 不同 app 之间尽量避免循环依赖。
6. 不要将所有内部 Service 函数都当作公开接口，只暴露真正需要跨模块使用的业务能力。

例如：

允许：调用 account 模块公开的业务服务。

```python
from backend.apps.account.services import get_user
```

不允许：直接访问 account 模块内部实现。

```python
from backend.apps.account.repositories.user import UserRepository
```

当某个业务模块复杂到需要区分内部服务和外部调用接口时，再考虑单独引入 `api.py` 或 Facade，不必提前增加这一层。

## 四、配置管理 config

```text
config/
├── __init__.py
├── settings.py
├── logging.py
└── constants.py
```

职责：

- `settings.py`：统一管理环境配置及运行参数。
- `logging.py`：日志配置。
- `constants.py`：全局通用常量。

约定：

- 通过统一配置入口读取环境变量。
- 不在业务模块中直接读取环境变量。
- 不同环境的配置通过环境变量或配置文件切换。
- 不将业务规则和业务常量放入全局配置模块。

## 五、通用能力 core

```text
core/
├── __init__.py
├── types.py
├── enums.py
├── context.py
├── security.py
├── pagination.py
├── datetime.py
└── utils/
```

职责：

存放与具体业务无关、可被多个业务模块复用的基础能力。

| 文件或目录 | 职责 |
|---|---|
| `types.py` | 通用类型定义 |
| `enums.py` | 全局通用枚举 |
| `context.py` | 请求上下文及运行上下文 |
| `security.py` | 无状态安全工具 |
| `pagination.py` | 通用分页结构与分页工具 |
| `datetime.py` | 日期时间处理工具 |
| `utils/` | 其他通用纯工具函数 |

约定：

- `core` 不依赖任何具体业务 app。
- 不将业务逻辑放入 `core`。
- 不为了代码复用而将所有公共函数都放入 `core`。
- `security.py` 仅存放无状态安全工具，例如密码哈希、Token 编解码等。
- 认证流程、用户身份管理和权限策略属于对应业务模块，例如 `apps/account`。

## 六、基础设施 infrastructure

```text
infrastructure/
├── __init__.py
│
├── database/
│   ├── __init__.py
│   ├── engine.py
│   ├── session.py
│   ├── base.py
│   └── models.py
│
├── cache/
│   ├── __init__.py
│   ├── clients.py
│   ├── keys.py
│   ├── deps.py
│   └── redis/                       # 具体缓存实现（按需拆分）
│       ├── __init__.py
│       ├── client.py
│       └── config.py
│
├── storage/
│   ├── __init__.py
│   ├── client.py
│   └── service.py
│
└── async_task/
    ├── __init__.py
    ├── broker.py
    └── scheduler.py
```

### 6.1 职责

| 目录 | 职责 |
|---|---|
| `database/` | 数据库连接、Session 生命周期及模型注册 |
| `cache/` | 缓存客户端及相关基础能力 |
| `storage/` | 文件存储客户端及存储操作封装 |
| `async_task/` | 异步任务 Broker、连接配置及调度基础能力 |

### 6.2 设计约定

基础设施负责提供技术能力，业务策略归属业务 app。

例如：

| 能力 | 所属位置 |
|---|---|
| 缓存客户端 | `infrastructure/cache/` |
| 验证码业务 | `apps/account/` |
| 文件存储实现 | `infrastructure/storage/` |
| 文件管理业务 | `apps/file/` |
| 异步任务运行能力 | `infrastructure/async_task/` |
| 具体异步任务 | `apps/<app>/tasks/` |

约定：

- 基础设施不依赖具体业务 app。
- 基础设施不直接承载业务策略。
- 技术实现尽量封装在对应目录内部。
- 业务模块通过基础设施提供的能力访问外部资源。
- 基础设施子模块的连接与运行参数定义在各自的 `config.py` 中，由全局配置（`config/settings.py`）聚合。

### 6.3 数据库约定

- 数据库 Engine 全局复用。
- Session 按请求或任务创建。
- 不在全局保存长期共享的 Session。
- 事务边界由业务用例明确控制。
- HTTP 请求与后台任务分别管理自己的 Session 生命周期。
- 不跨请求或任务共享 Session。
- 不将 Session 或数据库连接作为异步任务参数传递。
- 数据库迁移统一由根目录 `migrations/` 管理。

其中 `database/models.py` 用于统一导入所有业务模块的数据库模型，供 Alembic 识别。

例如：

```python
# infrastructure/database/models.py

from backend.apps.account.models import User
from backend.apps.ticket.models import Ticket
from backend.apps.notification.models import Notification
```

在 `migrations/env.py` 中导入统一注册模块，再使用对应的 metadata。

```python
from sqlmodel import SQLModel
from backend.infrastructure.database import models  # noqa: F401

target_metadata = SQLModel.metadata
```

新增业务模块时，需要将其数据库模型加入统一注册入口，否则 Alembic 自动生成迁移时可能遗漏相关表。

注意：模型注册模块只负责导入模型，不应触发业务初始化或其他运行时副作用。

### 6.4 事务与异步任务

- 普通业务场景：数据库事务提交后，再投递异步任务。
- 对任务可靠性要求较高的场景：考虑使用 Outbox 模式，解决数据库提交与消息投递之间的一致性问题。
- 后台任务自行创建和释放 Session，不复用 HTTP 请求中的 Session。

## 七、全局异常 errors

```text
errors/
├── __init__.py
├── base.py
├── codes.py
└── handlers.py
```

职责：

- `base.py`：全局异常基类。
- `codes.py`：全局错误码定义。
- `handlers.py`：全局异常处理器。

约定：

1. 全局错误码放在 `errors/codes.py`。
2. 业务错误码由各业务 app 自行定义。
3. 业务异常继承全局异常基类。
4. 全局异常模块不反向依赖具体业务模块。
5. 错误码统一采用整数或字符串，不混合使用。
6. 错误码可以按业务模块划分编号区间，避免重复。

例如：

```text
errors/
└── codes.py

apps/
├── account/
│   └── errors.py
└── ticket/
    └── errors.py
```

全局异常处理器负责统一转换异常响应，业务模块负责定义自身的业务异常。

## 八、接口层 presentation

```text
presentation/
├── __init__.py
└── http/
    ├── __init__.py
    ├── router.py
    ├── middleware.py
    └── deps.py
```

职责：负责 HTTP 接口的统一装配。

| 文件 | 职责 |
|---|---|
| `router.py` | 注册业务路由、统一配置路由前缀及版本 |
| `middleware.py` | 注册全局 HTTP 中间件 |
| `deps.py` | 定义全局 HTTP 依赖 |

约定：

- 业务路由由各自 app 的 `routes.py` 维护。
- 全局路由注册由 `presentation/http/router.py` 负责。
- URL 前缀及版本号由统一路由入口决定，例如 `/api/v1`。
- app 不负责全局路由注册和 URL 版本前缀。
- 中间件只负责通用 HTTP 处理，不承载具体业务流程。

## 九、命令行 cli

```text
cli/
├── __init__.py
├── app.py
└── commands/
    ├── __init__.py
    ├── database.py
    ├── user.py
    └── storage.py
```

职责：

- `app.py`：创建命令行应用。
- `commands/`：定义命令、参数解析及命令执行入口。
- 根目录 `manage.py`：统一命令行启动入口。

约定：

- CLI 负责命令行接口，不负责实现业务逻辑。
- 命令通过调用业务 Service 或可复用脚本完成操作。
- 不在 CLI 中重复实现业务规则。
- 命令参数解析和命令执行流程应保持简单。

## 十、后台任务 worker

```text
worker/
├── __init__.py
├── run.py
└── tasks.py
```

职责：

| 位置 | 职责 |
|---|---|
| `infrastructure/async_task/` | Broker 实例及连接配置 |
| `worker/run.py` | Worker 运行入口 |
| `worker/tasks.py` | 统一注册业务任务 |
| `apps/<app>/tasks/` | 定义具体业务任务 |

约定：

- 具体任务属于对应业务 app。
- Worker 负责任务注册与运行，不承载业务逻辑。
- `worker/tasks.py` 只负责导入各业务任务模块，完成任务注册。
- Scheduler 按需配置，不强制引入。
- 任务执行时自行管理数据库 Session 生命周期。

例如：

```text
apps/
├── account/
│   └── tasks/
│       ├── __init__.py
│       └── notification.py
└── ticket/
    └── tasks/
        ├── __init__.py
        └── reminder.py
```

## 十一、脚本 scripts 与运维 devops

脚本根据用途和作用范围划分。

| 位置 | 用途 |
|---|---|
| `apps/<app>/scripts/` | 业务模块专属维护脚本 |
| `src/backend/scripts/` | 跨业务模块的运行时维护、初始化及数据处理脚本 |
| 根目录 `devops/` | 部署、CI/CD、环境初始化及运维辅助脚本 |
| `cli/commands/` | 面向开发者或运维人员的命令行接口 |

约定：

- `scripts/` 存放可复用的操作逻辑。
- `cli/commands/` 负责提供命令行交互入口。
- CLI 可以调用 scripts 或业务 Service。
- `devops/` 不承载应用运行时业务逻辑。
- 避免同一业务逻辑在 CLI 和 scripts 中重复实现。

## 十二、测试 tests

### 12.1 目录结构

```text
tests/
├── conftest.py
│
├── unit/
│   └── apps/
│
├── integration/
│   ├── apps/
│   └── infrastructure/
│       ├── test_cache.py
│       └── test_storage.py
│
├── e2e/
│   └── test_user_registration.py
│
└── factories/
```

### 12.2 测试分类

| 类型 | 测试范围 |
|---|---|
| `unit/` | 单个函数、领域规则、业务逻辑及独立组件 |
| `integration/` | 数据库、缓存、存储及多个组件之间的集成 |
| `e2e/` | 从实际入口开始的完整业务流程 |
| `factories/` | 测试数据工厂及测试对象构造 |

具体约定：

- Unit 测试应尽量隔离外部依赖。
- Integration 测试验证组件之间的真实协作。
- E2E 测试验证完整业务流程。
- CLI 参数解析、独立任务逻辑等可以进行 Unit 测试。
- HTTP 路由与数据库集成通常归 Integration。
- Worker 任务注册与 Broker 集成通常归 Integration。
- 完整 HTTP、CLI 或 Worker 业务流程归 E2E。

**测试分类依据测试范围和外部依赖，而不是被测代码属于哪个目录。**

## 十三、Module 与 Package 组织约定

### 13.1 基本概念

- Module：单个 Python 模块，通常对应一个 `.py` 文件，负责相对独立的职责。
- Package：由多个模块组成的功能组织单元，通常对应一个目录。

### 13.2 拆分原则

初期优先使用单文件，只有职责独立且持续扩展时才拆分为同名 Package。

例如，初期：

```text
account/
├── routes.py
├── schemas.py
├── models.py
└── services.py
```

业务复杂后：

```text
account/
├── routes.py
├── schemas/
│   ├── __init__.py
│   ├── requests.py
│   └── responses.py
├── models.py
└── services/
    ├── __init__.py
    ├── registration.py
    └── authentication.py
```

约定：

- 不提前创建空目录。
- 单文件职责明确时，不强制拆分。
- 拆分后保持原有模块的公开导入接口尽量稳定。
- 不仅根据文件行数决定是否拆分。

行数可作为参考：

- 300～800 行：常见范围。
- 超过 1000 行：建议检查是否存在职责过多的问题。
- 行数不是硬性标准，职责边界才是主要依据。

## 十四、模块依赖原则

整体依赖关系遵循以下约定：

1. `core` 不依赖业务 app。
2. `infrastructure` 不依赖具体业务 app。
3. `apps` 不依赖 `presentation`。
4. `presentation` 负责接口装配，不承载业务逻辑。
5. `cli`、`worker` 作为独立运行入口，调用业务能力。
6. 不同 app 尽量通过公开的 `services.py` 接口交互。
7. 不允许跨 app 直接访问内部 Repository、Domain 和 Models。
8. 基础设施负责技术实现，业务 app 负责业务策略。
9. 避免模块之间形成循环依赖。
10. 通用能力应放在真正合适的公共模块中，不要为了复用而随意堆积到 `core`。

整体依赖关系：

```text
                  ┌───────────────┐
                  │   main.py     │
                  └───────┬───────┘
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
       presentation      cli         worker
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │   apps   │
                    └────┬─────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
             core             infrastructure
```

补充：这张图表达的是运行入口与业务能力的主要关系，不代表所有模块之间都允许任意调用。具体依赖仍应遵循前面的边界约定。

## 十五、最终架构定位

本项目采用：

**轻量模块化单体 + 业务域隔离 + 基础设施统一封装 + 多入口运行。**

核心设计原则：

| 设计方向 | 约定 |
|---|---|
| 业务组织 | 按业务域划分 app |
| 业务边界 | 通过公开 Service 接口交互 |
| 数据访问 | 按复杂度决定是否引入 Repository |
| 领域建模 | 按复杂度决定是否引入 Domain |
| 数据模型 | 数据库 Model 与 API Schema 分离 |
| 基础设施 | 统一封装外部技术能力 |
| HTTP 接口 | 统一装配，业务路由归属 app |
| 命令行 | 独立入口，复用业务能力 |
| 后台任务 | 统一运行入口，具体任务归属 app |
| 数据迁移 | 统一管理 |
| 测试 | 按测试范围与依赖分类 |
| 代码拆分 | 先模块化，后按需 Package 化 |

最终原则：

> 目录结构服务于职责边界，而不是为了目录本身增加抽象。
>
> 命名尽量保持技术无关，具体技术选型由基础设施内部实现。
>
> 优先保证业务模块之间的边界清晰，再根据实际复杂度逐步演进架构。
