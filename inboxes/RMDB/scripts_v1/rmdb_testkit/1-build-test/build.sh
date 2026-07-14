#!/usr/bin/env bash
# Step 1: 编译 server + client + unit_test
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RMDB_ROOT="${RMDB_ROOT:-$SCRIPT_DIR/../../..}"
BUILD="$RMDB_ROOT/build"
CLIENT_SRC="$RMDB_ROOT/rmdb_client"
CLIENT_BUILD="$CLIENT_SRC/build"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "==> 编译 rmdb server"
cmake --build "$BUILD" -j "$(nproc)"
if [[ -x "$BUILD/bin/rmdb" ]]; then
  echo -e "  ${GREEN}✓${NC} rmdb server"
else
  echo -e "  ${RED}✗${NC} $BUILD/bin/rmdb 不存在"
  exit 1
fi

echo "==> 编译 rmdb_client"
mkdir -p "$CLIENT_BUILD"
cmake -S "$CLIENT_SRC" -B "$CLIENT_BUILD" > /dev/null 2>&1
cmake --build "$CLIENT_BUILD" -j "$(nproc)"
if [[ -x "$CLIENT_BUILD/rmdb_client" ]]; then
  echo -e "  ${GREEN}✓${NC} rmdb_client"
else
  echo -e "  ${RED}✗${NC} rmdb_client 不存在"
  exit 1
fi

echo -e "${GREEN}编译完成${NC}"
