#!/usr/bin/env bash
# Step 6: 执行 TPC-C 压测
set -euo pipefail

BENCH="${BENCH:?}"
PORT="${PORT:?}"
W="${W:?}"
THREADS="${THREADS:?}"
WARMUP="${WARMUP:?}"
MEASURE="${MEASURE:?}"
ROUNDS="${ROUNDS:?}"
MINI="${MINI:-}"

echo "==> TPC-C 压测 (${ROUNDS} 轮, W=$W, ${THREADS} 线程)"

DRIVER_SCALE_ARGS=()
if [[ -n "$MINI" ]]; then
  DRIVER_SCALE_ARGS=(--customers 100 --orders 100 --items 1000)
fi

"$BENCH/tpcc_driver" -p "$PORT" -t "$THREADS" -w "$W" \
  --warmup "$WARMUP" --measure "$MEASURE" -r "$ROUNDS" \
  "${DRIVER_SCALE_ARGS[@]}"
