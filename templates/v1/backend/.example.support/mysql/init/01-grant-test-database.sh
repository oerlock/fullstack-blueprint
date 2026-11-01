#!/bin/bash
# 为应用用户授予测试库权限，供集成测试创建/重建测试数据库使用。
# 仅在 MySQL 数据目录首次初始化时由 docker-entrypoint 执行一次。

mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e \
  "GRANT ALL PRIVILEGES ON \`app_test%\`.* TO '${MYSQL_USER}'@'%'; FLUSH PRIVILEGES;"
