#!/usr/bin/env bash
# Step 2: 编译 TPC-C 压测驱动
set -euo pipefail

BENCH="${BENCH:?}"
DRIVER_DIR="$BENCH/02-driver"

echo "==> 编译 benchmark-driver"
g++ -O2 -std=c++17 -pthread \
  -I"$DRIVER_DIR" \
  "$DRIVER_DIR"/*.cpp \
  -o "$BENCH/tpcc_driver"
echo "  编译完成"
