#!/usr/bin/env bash
# perf 采样脚本：在 TPC-C 压测期间自动采集 rmdb 进程的性能数据。
# 由 run.sh Step 6 在 bench 启动后调用。
#
# 用法:
#   profile_bench_perf.sh --rmdb-pid <pid> --log-dir <dir> --warmup <s> --measure <s>
set -u

LOG_DIR=""
RMDB_PID=""
WARMUP=30
MEASURE=60

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rmdb-pid) RMDB_PID="$2"; shift 2;;
    --log-dir) LOG_DIR="$2"; shift 2;;
    --warmup) WARMUP="$2"; shift 2;;
    --measure) MEASURE="$2"; shift 2;;
    *) shift;;
  esac
done

if [[ -z "$RMDB_PID" || -z "$LOG_DIR" ]]; then
  echo "用法: $0 --rmdb-pid <pid> --log-dir <dir> --warmup <s> --measure <s>" >&2
  exit 1
fi

PERF_DIR="$LOG_DIR/perf"
mkdir -p "$PERF_DIR"

# 如果 perf 不可用，静默跳过
if ! command -v perf >/dev/null 2>&1; then
  echo "[perf] perf 不可用，跳过采样" | tee "$PERF_DIR/skip.txt"
  exit 0
fi

# 时序: warmup 结束后等 3s → 采集 → 提前 7s 结束
# 总等待 = warmup + 3s, 采集时长 = measure - 10s
PERF_DELAY=3
PERF_END_MARGIN=7
TOTAL_SLEEP=$((WARMUP + PERF_DELAY))
PERF_DURATION=$((MEASURE - PERF_DELAY - PERF_END_MARGIN))
if [[ $PERF_DURATION -lt 5 ]]; then
  PERF_DURATION=5
fi

echo "[perf] warmup=${WARMUP}s 结束后等 ${PERF_DELAY}s 开始采集, 采集 ${PERF_DURATION}s"
echo "[perf] 等待 warmup + delay = ${TOTAL_SLEEP}s..."

sleep "$TOTAL_SLEEP"

echo "[perf] perf record 开始 (pid=$RMDB_PID, duration=${PERF_DURATION}s)"
perf record -e cpu-clock -F 99 -g --call-graph dwarf,32768 \
  -p "$RMDB_PID" -o "$PERF_DIR/perf.data" \
  sleep "$PERF_DURATION" \
  >"$PERF_DIR/perf-record.out" 2>"$PERF_DIR/perf-record.err"
PERF_RC=$?

if [[ "$PERF_RC" -ne 0 ]]; then
  echo "[perf] perf record 失败 (rc=$PERF_RC)，详见 $PERF_DIR/perf-record.err"
  cat "$PERF_DIR/perf-record.err" 2>/dev/null
  exit 0  # perf 失败不影响压测结果
fi

echo "[perf] 生成 perf report..."
perf report -i "$PERF_DIR/perf.data" --stdio --sort=overhead,symbol \
  >"$PERF_DIR/perf_report.txt" 2>/dev/null || true

echo "[perf] 生成热点 Top-50..."
perf report -i "$PERF_DIR/perf.data" --stdio --sort=overhead -n --no-children \
  2>/dev/null | head -80 >"$PERF_DIR/perf_top.txt" || true

# 尝试生成火焰图
FLAMEGRAPH_DIR="${FLAMEGRAPH_DIR:-/opt/FlameGraph}"
if [[ -d "$FLAMEGRAPH_DIR" ]]; then
  echo "[perf] 生成火焰图..."
  perf script -i "$PERF_DIR/perf.data" > "$PERF_DIR/perf.script" 2>/dev/null || true
  if [[ -s "$PERF_DIR/perf.script" ]]; then
    "$FLAMEGRAPH_DIR/stackcollapse-perf.pl" "$PERF_DIR/perf.script" \
      > "$PERF_DIR/folded.stacks" 2>/dev/null || true
    "$FLAMEGRAPH_DIR/flamegraph.pl" "$PERF_DIR/folded.stacks" \
      > "$PERF_DIR/flamegraph.svg" 2>/dev/null || true
    if [[ -s "$PERF_DIR/flamegraph.svg" ]]; then
      echo "[perf] 火焰图: $PERF_DIR/flamegraph.svg"
    fi
  fi
else
  echo "[perf] FlameGraph 未安装 ($FLAMEGRAPH_DIR 不存在)，跳过火焰图"
fi

echo "[perf] 热点 Top-10:"
head -30 "$PERF_DIR/perf_top.txt" 2>/dev/null || true
echo "[perf] 完成，产物目录: $PERF_DIR"
