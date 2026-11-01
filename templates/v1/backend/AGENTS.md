使用 `backend/` 作为后台项目的根目录。

## 参考文档索引

| 规范文件                              | 适用场景         |
|---------------------------------------|------------------|
| `docs/standards/project_structure.md` | 后台目录结构设计 |
| `docs/standards/errors.md`            | 异常与错误处理   |
| `docs/standards/fastapi.md`           | FastAPI 编写偏好 |
| `docs/standards/database.md`          | 数据库设计与操作 |

## 工具（补充）

- 使用 [uv](https://docs.astral.sh/uv/) 管理 Python 包和项目。
- 临时文件存放在 `tmp/<YYYYMMDD>/`。

## 开发约定（补充）

- `scripts/` 存放全局脚本，`src/scripts/` 存放应用内脚本。
- 设计和实现必须考虑多实例部署。