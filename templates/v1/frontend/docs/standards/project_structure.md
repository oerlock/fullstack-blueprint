# 前端目录结构设计

基于 Vite + React + TypeScript 模板，采用 **业务模块优先（Feature-based）+ 技术职责分层（Layer-based）** 的组织方式。

核心原则：**优先保持简单，随着业务复杂度渐进式拆分。** 不预设不必要的架构层级，目录按需创建，职责清晰即可。

## 1. 项目目录结构

```text
frontend/
├── .support/                         # 本地运行支持文件（按需，Git Ignore）
│
├── devops/                           # 运维脚本与工程辅助工具
│   └── scripts/
│
├── docs/                             # 前端项目文档
│   ├── README.md                     # 文档索引
│   ├── standards/                    # 开发规范
│   ├── designs/                      # 架构与设计文档
│   ├── gotchas/                      # 踩坑记录
│   └── decisions/                    # 技术决策记录（ADR）
│
├── public/                           # 无需 Vite 处理的静态资源
│   └── runtime-config.js             # 运行时配置
│
├── src/                              # 核心源码
│   ├── app/                          # 应用入口与全局装配
│   │   ├── providers/                # 全局 Provider
│   │   ├── router/                   # 路由配置
│   │   ├── layouts/                  # 全局布局
│   │   ├── guards/                   # 路由守卫通用机制
│   │   ├── App.tsx
│   │   └── bootstrap.tsx             # 应用初始化与挂载
│   │
│   ├── assets/                       # 需要 Vite 处理的静态资源
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   │
│   ├── components/                   # 全局通用组件
│   │   ├── ui/                       # 基础 UI 组件
│   │   └── business/                 # 跨模块业务组件
│   │
│   ├── features/                     # 业务功能模块
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── user/
│   │
│   ├── generated/                    # Orval 自动生成代码
│   │   ├── api/                      # API 请求函数
│   │   ├── models/                   # API 数据模型（按需）
│   │   └── schemas/                  # 校验 Schema（按需）
│   │
│   ├── hooks/                        # 全局通用 Hooks
│   ├── services/                     # 全局基础服务
│   │   ├── http/                     # HTTP 客户端与拦截器
│   │   ├── storage/                  # 本地存储
│   │   └── websocket/                # WebSocket（按需）
│   │
│   ├── stores/                       # 全局共享状态
│   ├── lib/                          # 第三方库封装
│   ├── utils/                        # 通用工具函数
│   ├── types/                        # 全局类型定义
│   ├── constants/                    # 全局常量
│   ├── config/                       # 环境与运行时配置
│   ├── mocks/                        # MSW 接口 Mock
│   ├── tests/                        # 测试公共设施
│   │   ├── setup.ts                  # Vitest 全局初始化
│   │   ├── mocks/                    # 测试专用 Mock
│   │   └── utils/                    # 测试辅助工具
│   │
│   └── main.tsx                      # Vite 应用入口
│
├── .env                              # 本地环境变量（Git Ignore）
├── .env.example                      # 环境变量示例
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
├── vitest.config.ts                  # Vitest 测试配置
├── orval.config.ts                   # Orval 代码生成配置
├── eslint.config.js
├── .prettierrc
├── README.md
└── ...
```

## 2. 业务模块结构

业务代码优先归属于 `features/`，每个模块内部按需组织，不强制创建空目录。

例如：

```text
features/
└── user/
    ├── api/                          # 模块 API 封装
    ├── components/                   # 模块专属组件
    ├── hooks/                        # 模块专属 Hooks
    ├── pages/                        # 页面组件
    ├── stores/                       # 模块状态（按需）
    ├── types/                        # 模块类型（按需）
    ├── utils/                        # 模块工具函数（按需）
    ├── constants/                    # 模块常量（按需）
    └── index.ts                      # 模块公共出口
```

### 模块导出约定

- 模块对外只暴露明确允许共享的公共 API，通过 `index.ts` 统一导出。
- 其他模块禁止直接深层引用内部实现（如 `features/user/components/UserTable`）。
- 模块内部文件之间的引用不受此限制。
- 不要求导出模块内部所有内容，只暴露实际需要共享的组件、Hooks、类型等。
- 注意避免 barrel 文件引入循环依赖。

## 3. 目录职责约定

| 目录 | 职责 |
|---|---|
| `app/` | 应用初始化、路由、Provider、布局 |
| `components/` | 全局可复用组件 |
| `features/` | 业务模块及其内部实现 |
| `generated/` | Orval 自动生成的代码 |
| `hooks/` | 全局通用 Hooks |
| `services/` | HTTP、存储、通信等基础服务 |
| `stores/` | 全局共享状态 |
| `lib/` | 第三方库封装与适配 |
| `utils/` | 通用纯工具函数 |
| `types/` | 全局共享类型 |
| `constants/` | 全局共享常量 |
| `config/` | 环境与运行时配置 |
| `mocks/` | MSW 接口级 Mock，用于开发调试 |
| `tests/` | 全局测试辅助设施 |

## 4. Orval 约定

- `orval.config.ts`：维护 OpenAPI 文档地址、生成模式、输出路径等配置。
- `src/generated/`：统一存放自动生成的代码，不直接手动修改。
- 生成模式统一为：集中生成到 `src/generated/`，不按 Tag 拆分生成位置。
- `features/*/api/`：按业务模块组织和封装 API 调用。
- `services/http/`：提供统一 HTTP 客户端、拦截器、请求配置和错误处理。
- 根据生成配置，按需创建 `api/`、`models/`、`schemas/` 等子目录。

### 依赖方向

```text
features/*/api/
       │
       ▼
src/generated/api/
       │
       ▼
services/http/
```

- `services/http/` 提供底层 HTTP 能力。
- `generated/` 通过配置使用统一 HTTP 客户端。
- `features/*/api/` 组织业务接口调用。
- 基础服务不得反向依赖具体业务模块。

## 5. Vitest 约定

采用测试文件就近存放的方式，公共测试设施集中管理。

例如：

```text
features/
└── user/
    ├── components/
    │   ├── UserTable.tsx
    │   └── UserTable.test.tsx
    ├── hooks/
    │   ├── useUserList.ts
    │   └── useUserList.test.ts
    └── utils/
        ├── user.utils.ts
        └── user.utils.test.ts
```

公共测试设施：

```text
src/
├── mocks/                            # MSW 接口 Mock
│   ├── handlers/
│   ├── browser.ts
│   └── server.ts
│
└── tests/
    ├── setup.ts                      # Vitest 全局初始化
    ├── mocks/                        # 测试专用 Mock
    └── utils/                        # 测试辅助工具
```

约定：

- 单元测试和组件测试与源码就近存放。
- 测试文件统一使用 `.test.ts` 或 `.test.tsx`。
- `vitest.config.ts`：维护测试运行配置。
- `tests/setup.ts`：维护全局测试初始化。
- `tests/mocks/`：维护测试专用 Mock，如数据工厂、stub 等。
- `tests/utils/`：维护测试辅助函数。
- `src/mocks/`：统一管理 MSW 接口级 Mock，用于本地开发和接口模拟。
- MSW 根据运行环境分别使用 Browser Worker 和 Node Server。

## 6. 开发约定

1. **业务归属优先**：业务相关的 API、组件、Hooks、类型、状态等优先放在对应的 `features/` 模块中。
2. **优先保持简单**：不预设不必要的架构层级，随着业务复杂度渐进式拆分，避免过度设计。
3. **按需抽取公共代码**：只有被多个模块复用且具有明确公共职责的代码，才考虑抽取到全局目录。
4. **明确组件边界**：
   - `components/ui/`：Button、Input、Modal、Loading、Empty、Error 等基础组件。
   - `components/business/`：跨业务模块复用的业务组件。
   - `features/*/components/`：单模块专属组件。
5. **明确服务边界**：
   - `services/http/`：HTTP 客户端、拦截器、统一错误处理。
   - `features/*/api/`：具体业务接口及封装。
6. **区分全局与局部**：全局 Hooks、类型、常量和状态放在对应根目录；业务专属内容放在模块内部。
7. **区分状态类型**：
   - `stores/`：真正跨业务模块共享的客户端状态。
   - `features/*/stores/`：模块内部共享状态。
   - 组件内部状态使用 React State，不进入全局 Store。
   - 服务端数据及缓存优先使用服务端状态管理方案，不重复存储到全局 Store。
8. **明确工具边界**：
   - `lib/`：第三方库封装与适配。
   - `utils/`：与具体第三方库无关的通用纯工具函数。
   - 模块专属工具放在 `features/*/utils/`。
9. **生成代码与手写代码分离**：Orval 生成文件不直接修改，业务逻辑放在对应模块中。
10. **测试代码就近存放**：业务测试跟随业务模块，公共测试设施集中管理。
11. **入口职责分离**：`main.tsx` 只负责调用 `app/bootstrap.tsx`；应用挂载、Provider 和全局初始化统一放在 `bootstrap.tsx`。
12. **路由守卫与认证解耦**：`app/guards/` 只实现守卫通用机制；登录态判断和权限业务放在 `features/auth/`，由路由层组合调用。
13. **避免循环依赖**：明确模块公共出口和基础设施依赖方向，避免模块之间相互依赖。
14. **目录按需创建**：不预留空目录，不为简单功能引入不必要的抽象。

## 7. 文档目录

```text
docs/
├── README.md                         # 文档索引
├── standards/                        # 开发规范
├── designs/                          # 架构与技术设计
├── gotchas/                          # 问题与解决方案
└── decisions/                        # 技术决策记录
```

- `standards/`：约定开发过程中应该怎么做。
- `designs/`：描述系统架构与技术方案。
- `gotchas/`：记录已遇到的问题及解决方法。
- `decisions/`：记录重要技术决策及其原因。

## 8. 环境配置约定

- `.env`、`.env.*.local` 等本地配置文件纳入 Git Ignore。
- 提供 `.env.example` 作为环境变量模板。
- Vite 的 `VITE_` 前缀变量会暴露给浏览器，不得存放密钥等敏感信息。
- `public/runtime-config.js` 用于部署时注入运行时配置，由 `src/config/` 统一读取和管理。
- `public/` 仅存放不需要 Vite 构建处理的静态资源；需要构建优化的资源放在 `src/assets/`。

## 9. 架构演进原则

- **优先保持简单**：以当前实际需求为依据组织代码，不提前引入复杂架构。
- **渐进式拆分**：当模块职责增多、代码规模扩大或复用需求出现时，再拆分目录和抽象公共能力。
- **明确边界**：拆分的目的是降低耦合、明确职责，而不是单纯增加目录层级。
- **按需共享**：先在业务模块内部实现，确认存在稳定的跨模块复用需求后，再抽取到全局。
- **持续演进**：架构允许随着业务发展调整，通过技术决策记录（ADR）沉淀重要变更及其原因。