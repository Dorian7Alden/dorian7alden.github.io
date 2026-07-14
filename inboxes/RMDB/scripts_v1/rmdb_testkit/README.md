# RMDB 测试工具集

独立于 rmdb 仓库的测试工具，避免测试代码与项目代码冲突，跨分支切换时不受影响。

## 快速开始

```bash
# 一键测试：串行执行编译 → 单元测试 → 集成测试 → 性能压测
./run_test.sh

# 灵活选择步骤
./cli.sh --integration --suite quick      # 只跑集成测试
./cli.sh --bench --large -t 16            # 只跑性能压测
./cli.sh --from 3                         # 从第 3 步开始
./cli.sh --build                          # 只编译

# 查看完整选项
./cli.sh --help
```

## 目录结构

```
rmdb_testkit/
├── cli.sh                   # CLI 入口，接受参数（步骤选择/测试套件/压测规模）
├── run_test.sh              # 一键启动（等价于 cli.sh --all）
├── 1-build-test/            # Step 1: 编译
│   └── build.sh
├── 2-unit-test/             # Step 2: 官方单元测试（ctest + unit_test）
│   └── run.sh
├── 3-integration-test/      # Step 3: 自写集成测试（启动 server，发 SQL 验证）
│   ├── lib/                 #   公共库（Server 管理 / TCP 客户端 / 断言工具）
│   ├── cases/               #   测试用例（01~13，按编号顺序执行）
│   └── run.py               #   入口（支持 --suite / --test）
├── 4-bench-test/            # Step 4: TPC-C 性能压测
│   ├── 01-generate-data.py  #   生成数据
│   ├── 02-build-driver.sh   #   编译驱动
│   ├── 02-driver/           #   驱动源码（5 种事务 + 公共头文件 + main）
│   ├── 03-start-server.sh   #   清理环境 + 启动 server
│   ├── 04-create-tables.sql #   建表 DDL
│   ├── 05-load-data.sh      #   load CSV 入库
│   ├── 06-run-benchmark.sh  #   执行压测
│   ├── 07-collect-stats.sh  #   收集统计 + 日志扫描
│   ├── 08-post-check.py     #   正确性验证（一致性检查 + 崩溃恢复）
│   ├── run.sh               #   编排入口
│   └── table_data/          #   数据目录（按规模分子目录：W1 / W50 / W1-mini）
└── logs/                    # 测试日志（每次运行自动创建，已加入 .gitignore）
```

## 测试流程

```
Step 1  编译           cmake --build 产出 server + client + unit_test
Step 2  单元测试        ctest + unit_test 二进制，不启动 server
Step 3  集成测试        启动 server，通过 TCP 发 SQL，验证数据库行为正确
Step 4  性能压测        生成 TPC-C 数据 → 编译驱动 → 启动 server → load → 压测 → 统计 → (可选) 正确性验证
```

## 设计规范

### 命名规则

- **测试步骤目录**：`N-description/`，N 为 1~4 的数字编号，按执行顺序排列
- **步骤内文件**：`NN-description.ext`，NN 为两位数步骤编号（bench 内为 01-08），按执行顺序排列
- **集成测试用例**：`NN-description.py`，放在 `3-integration-test/cases/`，按依赖关系排列
- **压测驱动文件**：`NN-txn-name.cpp`，放在 `4-bench-test/02-driver/`，按事务频率排列

### 日志规范

`logs/` 目录已加入 `.gitignore`，不纳入版本管理。

**目录结构：**

```
logs/
├── RECORDS.md                      # 汇总记录表（所有历史测试一行一条）
└── 2026-07-04_01_main_a1b2c3d/     # 单次测试日志
    ├── summary.log                  #   简要报告（只看各步骤结果）
    ├── info.txt                     #   Git 信息 + 运行参数
    ├── 1-build.log                  #   编译完整输出（排查用）
    ├── 2-unit.log                   #   单元测试完整输出
    ├── 3-integration.log            #   集成测试完整输出
    ├── 4-bench.log                  #   性能压测完整输出
    ├── server.log / server.pid      #   server 运行日志与 PID
    ├── load.log                     #   建表 + load 输出
    └── execution_stats.txt          #   server 端统计详情
```
```

**日志目录命名：** `YYYY-MM-DD_NN_branch_hash`

| 组成部分 | 说明 |
|---------|------|
| `YYYY-MM-DD` | 测试日期 |
| `NN` | 当天序号，从 01 自动递增 |
| `branch` | Git 分支名（`/` 替换为 `-`） |
| `hash` | commit 短哈希 |

**两种日志：**

| 类型 | 文件 | 用途 |
|------|------|------|
| 简要 | `summary.log` | 只看各步骤 PASS/FAIL，日常快速确认 |
| 完整 | `1~4-*.log` | 每步完整输出，出问题时排查细节 |

**汇总记录表（`RECORDS.md`）：**

每次测试结束后自动追加一行到 `logs/RECORDS.md`，表格格式：

```
| 日期 | # | 分支 | Commit | 编译 | 单元 | 集成 | 压测 | tpmC | 耗时 |
|------|---|------|--------|------|------|------|------|------|------|
| 2026-07-04 | 01 | main | a1b2c3d | ✓ | ✓ | ✓ | ✓ | 12345.67 | 00:05:23 |
| 2026-07-04 | 02 | feat-x | e4f5g6h | ✓ | ✓ | ✗ | — | — | 00:01:15 |
```

- ✓ = 通过，✗ = 失败，— = 未执行
- tpmC 自动从压测日志提取；未执行压测则显示 —
- 一眼看出所有历史测试的成败和性能趋势

### Git 要求

- 运行测试前必须 commit 所有修改，否则 `cli.sh` 会拒绝执行
- 这确保日志目录名中的 commit hash 能准确回溯到被测代码版本

### 添加新测试

**集成测试**：

1. 在 `3-integration-test/cases/` 创建 `NN-description.py`
2. 实现 `run(repo, server)` 函数
3. 在 `run.py` 的 `CASES` 字典中注册

**性能压测步骤**：

1. 在 `4-bench-test/` 创建 `0X-description.sh`（或 `.py`）
2. 在 `run.sh` 中添加对应的 `run_step` 调用
3. 可选步骤（如 `08-post-check.py`）通过 `--check` 等标志控制是否执行

## 常用命令

```bash
# OJ 提测前一键评测（编译 + 单元 + 集成 + 压测）
./run_test.sh

# 快速正确性检查（编译 + 单元 + 集成 quick）
./cli.sh --build --unit --integration --suite quick

# 集成测试全部用例
./cli.sh --integration --suite full

# OJ 针对性测试
./cli.sh --integration --suite oj

# 性能压测 + 正确性验证（OJ 规模，带 --check 启用一致性检查 + 崩溃恢复）
./cli.sh --bench --large -t 16 --warmup 10 --measure 60 -r 1 --check

# 性能压测（OJ 规模，仅压测不做 post-check）
./cli.sh --bench --large -t 16 --warmup 10 --measure 60 -r 1

# 性能压测（极小冒烟）
./cli.sh --bench --mini -t 4 --warmup 2 --measure 3 -r 1

# 查看历史日志
ls logs/
cat logs/2026-07-04_01_main_a1b2c3d/info.txt
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `RMDB_ROOT` | 仓库根目录 | 自动推导为 testkit 上两级目录 |

