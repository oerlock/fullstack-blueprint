## 路由

- 公共 `prefix` 由顶层 Router 统一管理，业务 Router 尽量直接定义完整资源路径，减少多层 `prefix` 隐式拼接，便于调试和定位。
- `tags` 按业务领域设置；存在业务层级时，使用 `:` 表示层级关系，例如 `agent`、`agent:threads`，避免通过多层 Router 的 `tags` 继承表达层级。
