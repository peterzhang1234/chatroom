#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "启动 WebSocket 聊天室 (daphne)..."
daphne -b 0.0.0.0 -p 8000 challenge.asgi:application
