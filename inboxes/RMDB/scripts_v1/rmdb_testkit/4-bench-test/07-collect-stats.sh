#!/usr/bin/env bash
# Step 7: 收集 server 端统计 + 日志异常扫描
set -euo pipefail

CLIENT="${CLIENT:?}"
PORT="${PORT:?}"
LOG_DIR="${LOG_DIR:?}"
STATS_FILE="$LOG_DIR/execution_stats.txt"

echo "==> server 端统计"
# 显示关键指标摘要
echo "show execution_stats" | "$CLIENT" -p "$PORT" 2>/dev/null | \
  grep -E "commits|aborts=|abort_reasons|dml_errors|ww_breakdown|avg_commit|avg_scan|avg_lock|buffer|gc|flush|fsync|txn" || true

# 完整导出到文件，供事后深入分析
echo "show execution_stats" | "$CLIENT" -p "$PORT" 2>/dev/null > "$STATS_FILE" || true
echo "  完整统计已保存: $STATS_FILE"

echo ""
echo "==> server log 异常扫描"
if grep -qiE "assert|terminate|corruption|double free|segfault|InternalError" "$LOG_DIR/server.log" 2>/dev/null; then
  echo "⚠️  server log 含异常关键词:"
  grep -iE "assert|terminate|corruption|double free|segfault|InternalError" "$LOG_DIR/server.log" | head -5
else
  echo "  无异常"
fi
