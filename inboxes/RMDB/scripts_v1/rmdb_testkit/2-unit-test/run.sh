#!/usr/bin/env bash
# Step 2: 官方单元测试 (ctest + unit_test 二进制)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RMDB_ROOT="${RMDB_ROOT:-$SCRIPT_DIR/../../..}"
BUILD="$RMDB_ROOT/build"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0

echo "==> ctest"
if ctest --test-dir "$BUILD" --output-on-failure; then
  echo -e "  ${GREEN}✓${NC} ctest"
  PASS=$((PASS + 1))
else
  echo -e "  ${RED}✗${NC} ctest"
  FAIL=$((FAIL + 1))
fi

echo "==> unit_test"
rm -rf "$RMDB_ROOT/BufferPoolManagerTest_db"
if "$BUILD/bin/unit_test"; then
  echo -e "  ${GREEN}✓${NC} unit_test"
  PASS=$((PASS + 1))
else
  echo -e "  ${RED}✗${NC} unit_test"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "结果: $PASS PASS, $FAIL FAIL"
[[ "$FAIL" -eq 0 ]] || exit 1
