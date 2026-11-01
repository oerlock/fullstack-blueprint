#!/bin/bash

# reload 默认只匹配 *.py，需显式包含 .env 文件才能在配置变更时触发重载
uv run uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --reload-dir "src" \
  --reload-dir ".env.d" \
  --reload-include "*.env" \
