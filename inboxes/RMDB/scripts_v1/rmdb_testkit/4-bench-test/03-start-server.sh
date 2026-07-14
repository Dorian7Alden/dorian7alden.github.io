#!/usr/bin/env bash
# Step 3: 清理环境 + 启动 server
set -euo pipefail

BUILD="${BUILD:?}"
RMDB="${RMDB:?}"
PORT="${PORT:?}"
DB="${DB:?}"
LOG_DIR="${LOG_DIR:?}"
PID_FILE="$LOG_DIR/server.pid"

# 清理旧进程和数据库
pkill -9 -f "bin/rmdb $DB" 2>/dev/null || true
sleep 0.3
rm -rf "${BUILD:?}/$DB"

# 检查端口
if (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; then
  exec 3>&- 3<&-
  echo "!! 端口 $PORT 已被占用。请先停止已有 rmdb，再运行 bench。"
  exit 1
fi

# 启动
echo "==> 启动 server (db=$DB)"
( cd "$BUILD" && exec "$RMDB" "$DB" ) >"$LOG_DIR/server.log" 2>&1 &
echo $! > "$PID_FILE"

# 等待就绪
READY=0
for i in $(seq 1 50); do
  if ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "!! server 提前退出，详见 $LOG_DIR/server.log"
    tail -40 "$LOG_DIR/server.log"
    exit 1
  fi
  if (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; then
    exec 3>&- 3<&-
    READY=1
    break
  fi
  sleep 0.2
done

if [[ "$READY" -ne 1 ]]; then
  echo "!! server 未在超时时间内监听 $PORT，详见 $LOG_DIR/server.log"
  tail -40 "$LOG_DIR/server.log"
  exit 1
fi

echo "  server 已就绪 (pid=$(cat "$PID_FILE"))"
