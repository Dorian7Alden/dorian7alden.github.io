#!/usr/bin/env bash
# Step 5: 建表 + load CSV 数据
set -euo pipefail

BENCH="${BENCH:?}"
CLIENT="${CLIENT:?}"
PORT="${PORT:?}"
DATA="${DATA:?}"
OUTPUT_FILE="${OUTPUT_FILE:-0}"
LOG_DIR="${LOG_DIR:?}"

echo "==> 建表 + load 数据"

{
  cat "$BENCH/04-create-tables.sql"
  for t in warehouse item district stock customer history orders new_orders order_line; do
    echo "load $DATA/$t.csv into $t;"
  done
  [[ "$OUTPUT_FILE" -eq 1 ]] || echo "set output_file off"
} | "$CLIENT" -p "$PORT" >"$LOG_DIR/load.log" 2>&1

if grep -qiE "error|abort|failure" "$LOG_DIR/load.log"; then
  echo "!! 建表/load 出现错误，详见 $LOG_DIR/load.log:"
  grep -iE "error|abort|failure" "$LOG_DIR/load.log" | head
  exit 1
fi

echo "  建表 + load 完成"
