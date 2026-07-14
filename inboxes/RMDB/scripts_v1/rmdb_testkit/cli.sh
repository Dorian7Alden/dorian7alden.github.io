#!/usr/bin/env bash
# RMDB 测试工具集 CLI
# 用法: ./cli.sh [选项]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export RMDB_ROOT="${RMDB_ROOT:-$SCRIPT_DIR/../..}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
  cat <<'EOF'
用法: ./cli.sh [选项]

步骤选择:
  --all           执行全部步骤 (1→2→3→4→5, 含 perf 采集)
  --phase NAME    gate(1-3) / bench(4) / all(1-4) 快捷阶段
  --build         执行 Step 1: 编译
  --unit          执行 Step 2: 单元测试
  --integration   执行 Step 3: 集成测试
  --bench         执行 Step 4: 性能压测
  --from N        从第 N 步开始执行 (N=1..4)

集成测试选项 (--integration):
  --suite NAME    quick / mvcc / correct / oj / full (默认 quick)
  --test NAME     跑指定测试 (可多次指定)

性能压测选项 (--bench):
  -w N            仓库数 (默认 1)
  -t N            并发线程数
  --large         OJ 规模 (W=50)
  --mini          极小冒烟
  --warmup S      预热秒数
  --measure S     测量秒数
  -r N            轮数
  --keep-data     复用已有数据
  --check         bench 后跑正确性检查

其他:
  --profile       启用 perf 采样 (自动包含于 --all/--phase all)
  --help          显示帮助
EOF
}

# ---- 默认值 ----
DO_BUILD=""
DO_UNIT=""
DO_INTEGRATION=""
DO_BENCH=""
FROM_STEP=""
SUITE="quick"
TEST_NAMES=()
# bench 参数透传
BENCH_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0;;
    --all) DO_BUILD=1; DO_UNIT=1; DO_INTEGRATION=1; DO_BENCH=1; export DO_PROFILE=1; shift;;
    --build) DO_BUILD=1; shift;;
    --unit) DO_UNIT=1; shift;;
    --integration) DO_INTEGRATION=1; shift;;
    --bench) DO_BENCH=1; shift;;
    --from)
      FROM_STEP="$2"
      case "$FROM_STEP" in
        1) DO_BUILD=1; DO_UNIT=1; DO_INTEGRATION=1; DO_BENCH=1;;
        2) DO_UNIT=1; DO_INTEGRATION=1; DO_BENCH=1;;
        3) DO_INTEGRATION=1; DO_BENCH=1;;
        4) DO_BENCH=1;;
        *) echo "无效 --from 值: $FROM_STEP (应为 1..4)"; exit 1;;
      esac
      shift 2
      ;;
    --phase)
      PHASE="$2"
      case "$PHASE" in
        gate) DO_BUILD=1; DO_UNIT=1; DO_INTEGRATION=1;;
        bench) DO_BENCH=1;;
        all) DO_BUILD=1; DO_UNIT=1; DO_INTEGRATION=1; DO_BENCH=1;;
        *) echo "无效 --phase 值: $PHASE (应为 gate/bench/all)"; exit 1;;
      esac
      shift 2
      ;;
    --profile) export DO_PROFILE=1; shift;;
    --suite) SUITE="$2"; shift 2;;
    --test) TEST_NAMES+=("$2"); shift 2;;
    # bench 参数透传
    -w|-t|-r|--warmup|--measure)
      BENCH_ARGS+=("$1" "$2"); shift 2;;
    --large|--mini|--keep-data|--with-output-file|--validate-data-only|--check)
      BENCH_ARGS+=("$1"); shift;;
    *) echo "未知参数: $1"; usage; exit 1;;
  esac
done

# 没选任何步骤，默认 --all
if [[ -z "$DO_BUILD$DO_UNIT$DO_INTEGRATION$DO_BENCH" ]]; then
  DO_BUILD=1; DO_UNIT=1; DO_INTEGRATION=1; DO_BENCH=1
fi

# ---- Git 信息记录 ----
cd "$RMDB_ROOT"
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH="${GIT_BRANCH//\//-}"  # 分支名中的 / 替换为 -
GIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_DIRTY=$(git status --porcelain 2>/dev/null | head -1)

if [[ -n "$GIT_DIRTY" ]]; then
  echo -e "${RED}⚠ 工作区有未提交的修改，请先 commit 再测试。${NC}"
  echo "  git status:"
  git status --short
  exit 1
fi

# ---- 日志目录 (格式: YYYY-MM-DD_NN_branch_hash) ----
TODAY=$(date +%Y-%m-%d)
LOGS_ROOT="$SCRIPT_DIR/logs"

# 计算当天的序号
SEQ=1
for d in "$LOGS_ROOT"/"$TODAY"_*; do
  if [[ -d "$d" ]]; then
    dirname=$(basename "$d")
    # 提取 _ 后的两位数字: YYYY-MM-DD_NN_...
    num=$(echo "$dirname" | sed -n 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_\([0-9]\{2\}\)_.*/\1/p')
    if [[ -n "$num" && "$num" -ge "$SEQ" ]]; then
      SEQ=$((num + 1))
    fi
  fi
done
SEQ_STR=$(printf "%02d" "$SEQ")

LOG_DIR="$LOGS_ROOT/${TODAY}_${SEQ_STR}_${GIT_BRANCH}_${GIT_HASH}"
mkdir -p "$LOG_DIR"
export LOG_DIR

# 记录 git 信息到日志目录
{
  echo "时间:     $(date '+%Y-%m-%d %H:%M:%S')"
  echo "分支:     $GIT_BRANCH"
  echo "Commit:   $(git rev-parse HEAD 2>/dev/null)"
  echo "提交信息: $(git log -1 --oneline 2>/dev/null)"
  echo "参数:     $0 $*"
} > "$LOG_DIR/info.txt"

echo "日志目录: $LOG_DIR"
echo "分支: $GIT_BRANCH   commit: $GIT_HASH"

# ---- 辅助 ----
SCRIPT_START=$(date +%s)
PASS=0; FAIL=0
SUMMARY_LOG="$LOG_DIR/summary.log"

# 初始化简要日志
{
  echo "============================================"
  echo "  RMDB 测试报告"
  echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "  分支: $GIT_BRANCH"
  echo "  提交: $(git -C "$RMDB_ROOT" log -1 --oneline 2>/dev/null)"
  echo "============================================"
  echo ""
} > "$SUMMARY_LOG"

elapsed() {
  local e=$(($(date +%s) - SCRIPT_START))
  printf "[%02d:%02d:%02d]" $((e/3600)) $(((e%3600)/60)) $((e%60))
}

# ---- 步骤结果追踪 ----
declare -A STEP_STATUS
declare -A STEP_TOOK
for s in 1 2 3 4 5; do
  STEP_STATUS[$s]="—"
  STEP_TOOK[$s]=0
done

run_step() {
  local step="$1" desc="$2" log="$3"; shift 3
  local step_t0; step_t0=$(date +%s)
  echo ""
  echo -e "${CYAN}============================================${NC}"
  echo -e "${CYAN}  $(elapsed)  Step ${step}: ${desc}${NC}"
  echo -e "${CYAN}============================================${NC}"
  set +e +o pipefail
  "$@" 2>&1 | tee "$log" | sed 's/\x1b\[[0-9;]*m//g'
  local rc=${PIPESTATUS[0]}
  sed -i 's/\x1b\[[0-9;]*m//g' "$log"
  set -e -o pipefail
  local took=$(($(date +%s) - step_t0))
  STEP_TOOK[$step]=$took

  if [[ "$rc" -eq 0 ]]; then
    echo -e "${GREEN}$(elapsed)  Step ${step}: ${desc}  ✓ PASS${NC} (${took}s)"
    echo "$(elapsed)  Step ${step} ${desc}  ✓ PASS (${took}s)" >> "$SUMMARY_LOG"
    STEP_STATUS[$step]="✓"
    PASS=$((PASS + 1))
  else
    local err_msg; err_msg=$(tail -3 "$log" | tr '\n' ' ' | sed 's/^[[:space:]]*//')
    echo -e "${RED}$(elapsed)  Step ${step}: ${desc}  ✗ FAIL${NC} (${took}s)"
    echo "$(elapsed)  Step ${step} ${desc}  ✗ FAIL (${took}s)" >> "$SUMMARY_LOG"
    echo "       错误: ${err_msg}" >> "$SUMMARY_LOG"
    echo "       详情: ${log}" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"
    echo -e "${RED}--- 错误详情 (${log}) ---${NC}"
    tail -20 "$log"
    echo -e "${RED}--- 错误详情结束 ---${NC}"
    STEP_STATUS[$step]="✗"
    FAIL=$((FAIL + 1))
    return 1
  fi
}

# ---- 执行 ----
if [[ -n "$DO_BUILD" ]]; then
  run_step 1 "编译" "$LOG_DIR/1-build.log" \
    bash "$SCRIPT_DIR/1-build-test/build.sh" || exit 1
fi

if [[ -n "$DO_UNIT" ]]; then
  run_step 2 "单元测试" "$LOG_DIR/2-unit.log" \
    bash "$SCRIPT_DIR/2-unit-test/run.sh" || exit 1
fi

if [[ -n "$DO_INTEGRATION" ]]; then
  INTEG_ARGS=("--suite" "$SUITE" "--log-dir" "$LOG_DIR")
  for t in "${TEST_NAMES[@]}"; do
    INTEG_ARGS+=("--test" "$t")
  done
  run_step 3 "集成测试" "$LOG_DIR/3-integration.log" \
    python3 "$SCRIPT_DIR/3-integration-test/run.py" "${INTEG_ARGS[@]}" || exit 1
fi

if [[ -n "$DO_BENCH" ]]; then
  # bench 失败不阻断后续 Phase 5 复检；run_step 已记录 FAIL 状态
  run_step 4 "性能压测" "$LOG_DIR/4-bench.log" \
    bash "$SCRIPT_DIR/4-bench-test/run.sh" "${BENCH_ARGS[@]}" || true

  # perf 自动采集（在 bench 完成后的 Step 4 总结中报告）
  PERF_DIR="$LOG_DIR/perf"
  if [[ -f "$PERF_DIR/perf_top.txt" ]]; then
    echo ""
    echo -e "${CYAN}  perf 热点 Top-10:${NC}"
    head -30 "$PERF_DIR/perf_top.txt"
  fi
fi

# Step 5: 压测后回归复检（干净库重跑集成测试）
DO_POSTCHECK="${DO_POSTCHECK:-}"
if [[ -n "$DO_BENCH" ]]; then
  DO_POSTCHECK=1
fi

if [[ -n "$DO_POSTCHECK" ]]; then
  POSTCHECK_ARGS=("--suite" "full" "--log-dir" "$LOG_DIR")
  run_step 5 "压测后回归复检" "$LOG_DIR/5-postcheck.log" \
    python3 "$SCRIPT_DIR/3-integration-test/run.py" "${POSTCHECK_ARGS[@]}" || true
fi

# ---- 提取性能指标 ----
TPMC="—"
ABORT_RATE="—"
MAX_RSS="—"
PEAK_CPU="—"
AVG_CPU="—"
STEP_HOTSPOTS=""
if [[ -f "$LOG_DIR/4-bench.log" ]]; then
  TPMC=$(grep -oP 'FINAL tpmC.*=\s*\K[\d.]+' "$LOG_DIR/4-bench.log" 2>/dev/null || echo "—")
  ABORT_RATE=$(grep -oP 'abort rate = \K[\d.]+' "$LOG_DIR/4-bench.log" 2>/dev/null | tail -1 || echo "—")
  MAX_RSS=$(grep -oP 'peak_rss_gb: \K[\d.]+' "$LOG_DIR/4-bench.log" 2>/dev/null || echo "—")
  PEAK_CPU=$(grep -oP 'peak_cpu_pct: \K[\d.]+' "$LOG_DIR/4-bench.log" 2>/dev/null || echo "—")
  AVG_CPU=$(grep -oP 'avg_cpu_pct: \K[\d.]+' "$LOG_DIR/4-bench.log" 2>/dev/null || echo "—")
  # 提取 p99 最高的 5 个 SQL step
  STEP_HOTSPOTS=$(awk '
    /^step[[:space:]]+count[[:space:]]+p50.*p99/ { in_table=1; next }
    in_table && /^[[:alnum:]._-]+[[:space:]]+[0-9]+[[:space:]]+[0-9.]+[[:space:]]+[0-9.]+/ {
      name=$1; p99=$(NF);
      gsub(/[[:space:]]+$/, "", p99);
      if (p99+0 > 0) print p99, name;
    }
    in_table && /^$/ { in_table=0 }
  ' "$LOG_DIR/4-bench.log" | sort -rn | head -5 | awk '{ printf "  %6.1f ms  %s\n", $1, $2 }')
fi

# ---- 汇总 ----
{
  echo ""
  echo "============================================"
  echo "  结果: ${PASS} PASS, ${FAIL} FAIL  |  $(elapsed)"
  if [[ "$TPMC" != "—" ]]; then
    echo "  tpmC: ${TPMC}  |  abort-rate: ${ABORT_RATE}%  |  RSS峰值: ${MAX_RSS} GB"
    echo "  CPU: 峰值 ${PEAK_CPU}%  |  平均 ${AVG_CPU}%"
    if [[ -n "$STEP_HOTSPOTS" ]]; then
      echo "  SQL Step 热点 (p99 Top-5):"
      echo "$STEP_HOTSPOTS"
    fi
  fi
  echo "  日志: ${LOG_DIR}"
  echo "============================================"
} | tee -a "$SUMMARY_LOG"

# ---- 写入汇总记录表 ----
RECORDS="$LOGS_ROOT/RECORDS.md"
TOTAL_TOOK=$(($(date +%s) - SCRIPT_START))
TOTAL_STR=$(printf "%02d:%02d:%02d" $((TOTAL_TOOK/3600)) $(((TOTAL_TOOK%3600)/60)) $((TOTAL_TOOK%60)))
DIR_NAME=$(basename "$LOG_DIR")

if [[ ! -f "$RECORDS" ]]; then
  {
    echo "# RMDB 测试记录"
    echo ""
    echo "| 日期 | # | 分支 | Commit | 编译 | 单元 | 集成 | 压测 | 复检 | tpmC | abort% | RSS峰值 | 耗时 |"
    echo "|------|---|------|--------|------|------|------|------|------|------|--------|---------|------|"
  } > "$RECORDS"
fi

echo "| $TODAY | $SEQ_STR | $GIT_BRANCH | $GIT_HASH | ${STEP_STATUS[1]} | ${STEP_STATUS[2]} | ${STEP_STATUS[3]} | ${STEP_STATUS[4]} | ${STEP_STATUS[5]} | $TPMC | $ABORT_RATE | $MAX_RSS | $TOTAL_STR |" >> "$RECORDS"

echo ""
echo -e "简要报告: ${SUMMARY_LOG}"
echo -e "历史记录: ${RECORDS}"
[[ "$FAIL" -eq 0 ]] || exit 1
