# 全栈模板后台

## 快速开始

1. `uv sync --group dev`

2. 配置环境变量与本地支持文件

   - （可选）复制环境变量示例后，按实际情况更新：

     ```bash
     mkdir .env.d
     cp .example.env.d/app.env .env.d/app.env
     cp .example.env.d/mysql.env .env.d/mysql.env
     cp .example.env.d/test_app.env .env.d/test_app.env
     ```

   - （可选）复制 MySQL 配置与初始化脚本（仅首次建库时执行，用于授予测试库权限）：

     ```bash
     mkdir -p .support
     cp -r .example.support/mysql .support/mysql
     ```

3. 启动本地依赖服务（MySQL、Redis）

   ```bash
   docker compose -f deployment/dev.docker-compose.yaml up -d
   ```

4. 执行数据库迁移（本地开发库）

   ```bash
   uv run alembic upgrade head
   ```

5. 启动服务: `./devops/dev.sh`

## 测试

```bash
# 全量测试（无外部依赖，数据库/Redis 集成测试自动跳过）
uv run pytest

# 需要真实 MySQL / Redis 的集成测试
uv run pytest --with-database --with-redis
```

测试环境变量（测试库名、Redis 测试 DB 号等）统一在 `.env.d/test_app.env` 覆盖。

## 管理命令

统一入口为 `manage.py`：

```bash
uv run python manage.py --help
```