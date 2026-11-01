# 20261101 目录结构重做

## 主题

按 `docs/standards/project_structure.md` 一次性迁移前端目录结构，不兼容旧结构。
设计文档见 [`../../restructure-20261101.md`](../../restructure-20261101.md)。

## 变更

- `src/api/{request,query-client,error}.ts` → `src/services/http/`，`src/config.ts` → `src/config/index.ts`。
- Orval 生成迁移至 `src/generated/`，模式由 `tags-split` 改为 `single` 集中生成。
- 新增 `app/` 骨架：`main.tsx` 薄入口 + `bootstrap.tsx`、`providers/`、`router/`（TanStack Router 代码式路由）、`layouts/`。
- 演示页迁移为 `features/home/`，新增 `features/health/api/` 封装。
- 样式归位 `assets/styles/`，新增 `src/mocks/`（MSW）与 `src/tests/setup.ts`。
