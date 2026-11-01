# 分支管理规范

## 1. 分支类型

采用 `main + dev` 双长期分支模式，配合临时开发分支和发布分支。

| 分支 | 职责 |
|---|---|
| `main` | 稳定分支，存放经过验证、可供使用的模板 |
| `dev` | 集成分支，用于集成和验证模板变更 |
| `feature/*` | 新增模板能力 |
| `fix/*` | 修复模板问题 |
| `refactor/*` | 优化模板结构和实现 |
| `docs/*` | 文档维护 |
| `test/*` | 测试维护 |
| `chore/*` | 依赖、构建及工程配置维护 |
| `release/*` | 发布准备与验证 |

## 2. 分支命名

临时分支统一使用以下格式：

```text
<type>/<scope>-<summary>
```

示例：

```text
feature/template-v2
fix/backend-config
refactor/frontend-structure
docs/project-structure
test/backend-template
chore/update-dependencies
release/v1.0.0
```

命名要求：

- 使用小写英文。
- 使用连字符 `-` 分隔单词。
- 名称简洁，能够体现任务范围和目的。

## 3. 开发流程

### 3.1 日常开发

- 临时分支从最新的 `main` 创建。
- 完成开发后，通过 Pull Request 合并到 `dev`。
- `dev` 用于集成验证，不直接用于正式发布。

```text
main
 ├── feature/*
 ├── fix/*
 ├── refactor/*
 └── docs/*
          │
          ▼
         dev
```

### 3.2 模板架构升级

不同代际的模板独立维护，统一放在 `templates/` 下。

```text
templates/
├── v1/
├── v2/
└── v3/
```

约定：

- 新一代模板应是一份完整、独立的工程模板。
- 已发布的旧代际模板原则上保留。
- 新一代模板不要求兼容旧代际的内部结构。
- 不同代际的模板可以根据实际需要独立修复和维护。

### 3.3 版本发布

发布时从 `main` 创建发布分支，选择性合并本次计划发布的变更。

```text
main
  │
  ▼
release/v1.0.0
  │
  ▼
验证与修复
  │
  ▼
Pull Request
  │
  ▼
main
  │
  ▼
Git Tag: v1.0.0
  │
  ▼
GitHub Release
```

约定：

- 发布分支从 `main` 创建。
- 只纳入本次计划发布的变更，不直接合并整个 `dev`。
- 发布前完成模板安装、构建及必要测试。
- 发布分支中的修复应同步到 `dev`。
- 发布完成后删除临时发布分支，保留 Git Tag。

## 4. 版本管理

区分模板代际和仓库发布版本：

| 类型 | 示例 | 说明 |
|---|---|---|
| 模板代际 | `templates/v1/`、`templates/v2/` | 工程架构的阶段性演进 |
| 仓库版本 | `v1.0.0`、`v1.1.0` | 整个仓库的发布记录 |

仓库版本采用语义化版本号：

```text
v<major>.<minor>.<patch>
```

- `major`：重大架构演进或不兼容变更。
- `minor`：新增模板能力或兼容性改进。
- `patch`：问题修复和小范围维护。

模板代际与仓库版本不要求一一对应。

## 5. Pull Request 规范

- 所有分支合并通过 Pull Request 完成。
- 禁止直接向 `main`、`dev` 和 `release` 推送代码。
- PR 应说明变更目的、内容及影响的模板代际。
- 合并前通过必要的检查和测试。
- 优先使用 Squash and merge，保持提交历史简洁。

## 6. 核心原则

1. `main` 保持稳定，`dev` 负责集成验证。
2. 临时分支从 `main` 创建，通过 PR 合并到目标分支。
3. 发布分支从 `main` 创建，选择性纳入发布内容。
4. 不将整个 `dev` 合并到 `release`。
5. 不同代际的模板独立维护，旧版本原则上保留。
6. 正式版本通过 Git Tag 和 GitHub Release 发布。
7. 优先保持分支管理简单，避免不必要的长期分支。