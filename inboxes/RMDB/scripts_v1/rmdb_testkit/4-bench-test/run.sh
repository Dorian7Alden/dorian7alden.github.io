#!/usr/bin/env bash
# TPC-C 性能压测编排：依次执行 01→07 步。
set -u

usage() {
  cat <<'EOF'
用法: ./run.sh [选项]

选项:
  -w N        仓库数 (默认 1；--large 时默认 50)
  -t N        并发线程数 (默认 16)
  --warmup S  预热秒数 (默认 30)
  --measure S 测量秒数 (默认 360)
  -r N        轮数 (默认 3)
  --mini      极小数据集 (秒级冒烟)
  --large     OJ 规模 (W=50)
  --keep-data 复用已有数据
  --validate-data-only 只生成/校验数据，不启动 server
  --with-output-file 保留 output.txt 写入
  --check     bench 后跑正确性检查
  --help      显示帮助

例:
  ./run.sh --mini -t 4 --warmup 2 --measure 3 -r 1
  ./run.sh --large -t 16
EOF
}

# ---- 全局变量 ----
BENCH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export RMDB_ROOT="${RMDB_ROOT:-$BENCH/../../..}"
export BUILD="$RMDB_ROOT/build"
export DB="tpcc_bench_db"
export PORT=8765
export RMDB="$BUILD/bin/rmdb"
export CLIENT="$RMDB_ROOT/rmdb_client/build/rmdb_client"

# ---- 参数解析 ----
W=1; W_EXPLICIT=""; THREADS=16; WARMUP=30; MEASURE=360; ROUNDS=3
MINI=""; KEEP=""; OUTPUT_FILE=0; LARGE=""
VALIDATE_ONLY=""; LOG_DIR="${LOG_DIR:-$BENCH/../logs/bench}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -w) W="$2"; W_EXPLICIT=1; shift 2;;
    -t) THREADS="$2"; shift 2;;
    --warmup) WARMUP="$2"; shift 2;;
    --measure) MEASURE="$2"; shift 2;;
    -r) ROUNDS="$2"; shift 2;;
    --mini) MINI="--mini"; shift;;
    --keep-data) KEEP=1; shift;;
    --with-output-file) OUTPUT_FILE=1; shift;;
    --help|-h) usage; exit 0;;
    --large) LARGE=1; shift;;
    --validate-data-only) VALIDATE_ONLY=1; shift;;
    --log-dir) LOG_DIR="$2"; mkdir -p "$LOG_DIR"; shift 2;;
    *) echo "未知参数: $1"; usage; exit 1;;
  esac
done

[[ -n "$LARGE" && -z "$W_EXPLICIT" ]] && W=50
[[ -x "$RMDB" ]] || { echo "找不到 $RMDB，请先编译 server"; exit 1; }
[[ -x "$CLIENT" ]] || { echo "找不到 $CLIENT，请先编译 rmdb_client"; exit 1; }

# 数据目录名
data_dir_name() {
  local w="$1"
  if [[ -n "$MINI" ]]; then echo "W${w}-mini"; else echo "W${w}"; fi
}
export DATA="$BENCH/table_data/$(data_dir_name "$W")"

# 导出供步骤脚本使用
export BENCH W THREADS WARMUP MEASURE ROUNDS MINI OUTPUT_FILE LOG_DIR DATA

# ---- 数据校验 ----
validate_tpcc_data() {
  local cust_per_dist=3000 stock_per_ware=100000
  [[ -n "$MINI" ]] && { cust_per_dist=100; stock_per_ware=1000; }

  local required=(warehouse district customer history orders new_orders order_line item stock)
  for t in "${required[@]}"; do
    [[ -f "$DATA/$t.csv" ]] || { echo "!! 缺少数据文件: $DATA/$t.csv"; return 1; }
  done

  local wh="$(head -n1 "$DATA/warehouse.csv")"
  [[ "$wh" == "w_id,w_name,w_street_1,w_city,w_state,w_zip,w_tax,w_ytd" ]] || { echo "!! warehouse.csv 表头不匹配"; return 1; }

  local wr; wr="$(wc -l < "$DATA/warehouse.csv")"
  local dr; dr="$(wc -l < "$DATA/district.csv")"
  local cr; cr="$(wc -l < "$DATA/customer.csv")"
  local sr; sr="$(wc -l < "$DATA/stock.csv")"
  local lw; lw="$(awk -F, 'END {print $1}' "$DATA/warehouse.csv")"

  [[ "$wr" -eq $((W + 1)) ]] || { echo "!! warehouse 行数不匹配: got=$wr expected=$((W + 1))"; return 1; }
  [[ "$dr" -eq $((W * 10 + 1)) ]] || { echo "!! district 行数不匹配: got=$dr expected=$((W * 10 + 1))"; return 1; }
  [[ "$cr" -eq $((W * 10 * cust_per_dist + 1)) ]] || { echo "!! customer 行数不匹配"; return 1; }
  [[ "$sr" -eq $((W * stock_per_ware + 1)) ]] || { echo "!! stock 行数不匹配"; return 1; }
  [[ "$lw" -eq "$W" ]] || { echo "!! 最后一个 w_id 不匹配: got=$lw expected=$W"; return 1; }
}

# ---- 进度输出 ----
SCRIPT_START=$(date +%s)
GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

elapsed() {
  local e=$(($(date +%s) - SCRIPT_START))
  printf "[%02d:%02d:%02d]" $((e/3600)) $(((e%3600)/60)) $((e%60))
}

run_step() {
  local step="$1" desc="$2"; shift 2
  local t0; t0=$(date +%s)
  echo -e "$(elapsed) [${step}/7] $desc..."
  if "$@"; then
    local took=$(($(date +%s) - t0))
    echo -e "$(elapsed) [${step}/7] $desc                        ${GREEN}✓${NC} (${took}s)"
  else
    local took=$(($(date +%s) - t0))
    echo -e "$(elapsed) [${step}/7] $desc                        ${RED}✗${NC} (${took}s)"
    exit 1
  fi
}

# ---- 清理 ----
cleanup() {
  local pid_file="$LOG_DIR/server.pid"
  if [[ -f "$pid_file" ]]; then
    local pid; pid=$(cat "$pid_file")
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -INT "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  fi
}
trap cleanup EXIT

# ================================================================
# Step 1: 生成数据
# ================================================================
step_1_generate() {
  if [[ -z "$KEEP" ]]; then
    rm -rf "$DATA" && mkdir -p "$DATA"
    python3 -u "$BENCH/01-generate-data.py" --warehouses "$W" --out "$DATA" $MINI
  else
    echo "  复用已有数据 (W=$W $MINI)"
    if ! validate_tpcc_data 2>/dev/null; then
      echo "  数据校验失败，自动重新生成..."
      rm -rf "$DATA" && mkdir -p "$DATA"
      python3 -u "$BENCH/01-generate-data.py" --warehouses "$W" --out "$DATA" $MINI
    fi
  fi
  validate_tpcc_data
}
run_step 1 "生成数据 (W=$W)" step_1_generate

[[ -n "$VALIDATE_ONLY" ]] && { echo "数据校验完成"; exit 0; }

# ================================================================
# Step 2: 编译驱动
# ================================================================
run_step 2 "编译驱动" bash "$BENCH/02-build-driver.sh"

# ================================================================
# Step 3: 启动 server
# ================================================================
run_step 3 "启动 server" bash "$BENCH/03-start-server.sh"

# ================================================================
# Step 4: 建表 DDL（无操作，SQL 文件在 Step 5 中使用）
# ================================================================
echo -e "$(elapsed) [4/7] 建表 DDL                           ${GREEN}✓${NC}"

# ================================================================
# Step 5: load 数据
# ================================================================
run_step 5 "load 数据" bash "$BENCH/05-load-data.sh"

# ================================================================
# Step 6: 执行压测（含 RSS 峰值监控）
# ================================================================
step_6_benchmark() {
  local pid_file="$LOG_DIR/server.pid"
  local rss_file="$LOG_DIR/rss.log"
  local cpu_file="$LOG_DIR/cpu.log"
  local mon_stop="$LOG_DIR/mon.stop"
  local pid; pid=$(cat "$pid_file" 2>/dev/null || echo "")

  # 启动资源监控（每秒采样 RSS + CPU%，标记文件出现时停止）
  if [[ -n "$pid" ]]; then
    rm -f "$rss_file" "$cpu_file" "$mon_stop"
    (
      max_rss=0
      while [[ ! -f "$mon_stop" ]]; do
        rss=$(ps -o rss= -p "$pid" 2>/dev/null || echo 0)
        [[ "$rss" -gt "$max_rss" ]] && max_rss=$rss
        cpu=$(ps -o %cpu= -p "$pid" 2>/dev/null || echo 0)
        cpu=${cpu:-0}
        echo "$cpu" >> "$cpu_file"
        sleep 1
      done
      echo "$max_rss" > "$rss_file"
      # 一次性计算 CPU 峰值和均值（浮点精度）
      awk '{ sum += $1; if ($1+0 > max+0) max = $1+0 } END { printf "%.1f\n", max; printf "%.1f", sum/NR }' \
        "$cpu_file" > "$cpu_file.peak_avg"
    ) &
    MONITOR_PID=$!
  fi

  # 启动 perf 后台采集（自动：warmup 结束后 measure 开始后采集）
  PERF_PID=""
  if [[ -n "${DO_PROFILE:-}" ]]; then
    bash "$BENCH/profile_bench_perf.sh" \
      --rmdb-pid "$pid" \
      --log-dir "$LOG_DIR" \
      --warmup "$WARMUP" \
      --measure "$MEASURE" &
    PERF_PID=$!
  fi

  # 执行压测
  bash "$BENCH/06-run-benchmark.sh"
  local bench_rc=$?

  # 等待 perf 完成
  if [[ -n "$PERF_PID" ]]; then
    wait "$PERF_PID" 2>/dev/null || true
  fi

  # 停止监控
  if [[ -n "${MONITOR_PID:-}" ]]; then
    touch "$mon_stop"
    wait "$MONITOR_PID" 2>/dev/null || true
    rm -f "$mon_stop"
  fi

  # 输出资源指标
  if [[ -f "$rss_file" ]]; then
    local peak_rss_kb; peak_rss_kb=$(cat "$rss_file"); peak_rss_kb=${peak_rss_kb:-0}
    awk -v kb="$peak_rss_kb" 'BEGIN { printf "peak_rss_gb: %.3f\n", kb / 1048576 }'
    rm -f "$rss_file"
  fi
  if [[ -f "$cpu_file.peak_avg" ]]; then
    local peak_cpu; peak_cpu=$(head -1 "$cpu_file.peak_avg"); peak_cpu=${peak_cpu:-0}
    local avg_cpu; avg_cpu=$(tail -1 "$cpu_file.peak_avg"); avg_cpu=${avg_cpu:-0}
    printf "peak_cpu_pct: %.1f\n" "$peak_cpu"
    printf "avg_cpu_pct: %.1f\n" "$avg_cpu"
    rm -f "$cpu_file" "$cpu_file.peak_avg"
  fi
  return $bench_rc
}
run_step 6 "TPC-C 压测 (${ROUNDS} 轮, W=$W, ${THREADS} 线程)" step_6_benchmark

# ================================================================
# Step 7: 收集统计
# ================================================================
run_step 7 "收集统计 + 日志扫描" bash "$BENCH/07-collect-stats.sh"

# ================================================================
# Step 8: 正确性验证（默认启用）
#   1. 一致性检查：行数 / 引用完整性 / 业务约束
#   2. 崩溃恢复：kill -9 → 重启 → 再次一致性检查
# ================================================================
step_8_post_check() {
  echo "==> bench 后正确性验证"
  python3 -u "$BENCH/08-post-check.py" --port "$PORT" --data-dir "$DATA" --W "$W" --log-dir "$LOG_DIR"
}
run_step 8 "正确性验证" step_8_post_check

# ---- 完成 ----
echo ""
echo "============================================"
echo "  耗时: $(elapsed)"
echo "============================================"
