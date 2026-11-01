- `sonner`：React 的 toast/通知组件。你这里的 <Toaster /> 是通知挂载点，后面可以在任意地方调用 toast(...) 弹消息。
- `lucide-react`：Lucide 的 React 图标包。每个图标都是独立 React 组件，底层是 SVG，可调大小、颜色、线宽，而且按需引入。官方文档：https://lucide.dev/guide/react
- `@base-ui/react`：Base UI 的 React 无样式组件库。提供 Dialog、Popover、Select、Combobox、Menu、Tooltip 等组件的交互逻辑、状态管理、键盘操作、焦点管理和可访问性支持，不绑定具体视觉样式，方便使用 Tailwind CSS 或 CSS Variables 自定义 UI。
- `zustand`：轻量级 React 状态管理库。用 create 定义一个 store 后，组件里直接通过 hook 读取和更新状态，不需要 Provider。官方文档：https://zustand.docs.pmnd.rs/getting-started/introduction
- `@uppy/core`：Uppy 的核心文件管理与上传状态管理模块。负责文件添加、删除、列表管理、文件元数据、上传进度、状态维护、限制校验以及事件通知，并通过插件机制扩展具体的上传能力。
- `@tanstack/react-router`：TanStack Router 的 React 路由库。负责应用的路由定义、页面导航、嵌套路由、动态路由参数、Search Params 和路由级数据加载，并提供完整的 TypeScript 类型推导。它主要负责“页面和 URL 之间的路由管理”。

## API 相关

- `@tanstack/react-query`：管理后端数据的请求状态、缓存、重试和刷新。业务组件使用 Orval 生成的 Query hooks 获取和更新数据，属于运行时依赖。
- `orval`：根据 OpenAPI 文档生成 TypeScript 类型、请求函数和 TanStack Query hooks，只在开发和 CI 生成代码时使用，属于开发依赖。

## 测试相关

- `vitest`：测试运行器，和 Vite 原生集成，负责执行单元测试、组件测试，并提供 `describe`、`test`、`expect`、mock 等测试能力。
- `@testing-library/react`：React 组件测试工具，强调从用户视角测试组件行为，而不是测试组件内部实现。常用 `render()`、`screen` 等 API 来查找元素和验证 UI。
- `@testing-library/jest-dom`：为 Vitest 等测试框架提供更适合 DOM 的断言，例如 `toBeInTheDocument()`、`toBeVisible()`、`toHaveTextContent()` 等，让 UI 测试更直观。
- `@testing-library/user-event`：模拟真实用户交互，例如点击、输入、键盘操作、Tab 切换等。相比直接触发 DOM 事件，更接近用户实际操作。
- `msw`：Mock Service Worker，用于拦截前端发出的 HTTP 请求并返回模拟响应。适合测试 API 请求、Loading、错误、空数据等状态，而不需要依赖真实后端服务。
- `jsdom`：提供浏览器 DOM 环境，供组件测试使用。
