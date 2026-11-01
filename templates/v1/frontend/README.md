# 全栈模板前端

## 配置优先级

应用配置统一通过 `src/config/index.ts` 读取，按以下优先级生效：

1. `public/runtime-config.js` 中的 `window.__APP_CONFIG__`（运行时配置）
2. `.env` 中的 `VITE_*` 变量（构建时配置）
3. 代码默认值

运行时配置文件会在应用入口之前由 `index.html` 加载。部署时可以只替换
`public/runtime-config.js`，复用同一份构建产物；该文件中的值会覆盖构建时的
`.env` 值。不要在其中放置密钥，因为它会发送到浏览器。

新增配置项时，请先在 `src/config/index.ts` 中声明类型、定义优先级和默认值，业务代码
只从 `config` 对象读取，不要直接访问 `import.meta.env` 或 `window.__APP_CONFIG__`。

## 后端 API

接口类型、请求函数和 TanStack Query hooks 根据 `openapi/api.json` 自动生成到
`src/generated/`，业务模块通过 `features/*/api/` 封装调用。业务代码使用封装的
hooks，不要直接调用 `fetch`、重复定义接口类型或修改生成代码。

更新 OpenAPI 快照并生成 API 代码：

```bash
npm run api:update
```

详细说明参见 [`docs/designs/infrastructure/api/overview.md`](docs/designs/infrastructure/api/overview.md)。

## 技能安装推荐

- [playwright](https://playwright.dev/agent-cli/skills)

  ```sh
  npm install -g @playwright/cli@latest
  playwright-cli install --skills=agents
  ```
