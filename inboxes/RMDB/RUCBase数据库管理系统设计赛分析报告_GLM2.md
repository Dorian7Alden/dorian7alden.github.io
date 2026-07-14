# 2026 RUCBase 比赛总分析报告（最终版）

> **报告版本**：v5.0（最终整合版）
> **生成日期**：2026-07-04
> **整合范围**：开源项目深度分析 + 获奖项目 Git 历史挖掘 + 团队文档体系解析 + 团队源码逐行验证
> **数据来源**：
> - Kosthi/CSCC-DB-Rucbase-2024 仓库（290 条 git 提交，17 分支）
> - RushDB-Lab/CSCC-DB-Rucbase-2025 仓库（源码 + README）
> - 团队上传 `2026-rmdb-docs.zip`（5 个子目录 50+ 篇文档）
> - 团队上传 `2026-our-源码.zip`（src/ 全量源码，逐文件验证）
> **核心目标**：为团队提供从当前 409 tpmC 到决赛高分的完整闭环指南

---

## 目录

- [第零部分：执行摘要](#第零部分执行摘要)
- [第一部分：研究方法论与数据来源](#第一部分研究方法论与数据来源)
- [第二部分：历届获奖项目深度分析](#第二部分历届获奖项目深度分析)
- [第三部分：获奖项目 Git 历史经验挖掘](#第三部分获奖项目-git-历史经验挖掘)
- [第四部分：团队现状全景诊断](#第四部分团队现状全景诊断)
- [第五部分：源码级深度验证（12 项关键发现）](#第五部分源码级深度验证12-项关键发现)
- [第六部分：团队 vs 历届获奖项目对比](#第六部分团队-vs-历届获奖项目对比)
- [第七部分：可借鉴与不可借鉴清单](#第七部分可借鉴与不可借鉴清单)
- [第八部分：优化方案全集（40+ 条）](#第八部分优化方案全集40-条)
- [第九部分：源码级实施指南（精确到行）](#第九部分源码级实施指南精确到行)
- [第十部分：备赛路线图与时间线](#第十部分备赛路线图与时间线)
- [第十一部分：风险管理与应对](#第十一部分风险管理与应对)
- [第十二部分：总结与核心建议](#第十二部分总结与核心建议)
- [附录](#附录)

---

# 第零部分：执行摘要

## 0.1 一句话结论

> **团队当前 tpmC=409 的根本原因不是文档说的"buffer_mutex + 同步 fsync + 执行锁过大"，而是"显式事务被强制串行化（`kExplicitTxnAdmissionLimit=1`）+ 无编译优化（默认 -O0）+ UPDATE 不支持列自引用"。仅放开串行化 + 开 -O3 + 修复 UPDATE 列自引用这 3 项改动，预期可让 tpmC 从 409 跃升到 2000~3000（5~7x）。**

## 0.2 核心数据速览

| 维度 | 数值 | 来源 |
|------|------|------|
| 团队当前 tpmC | **409.67** | 团队性能提升实施方案 §1 |
| 原始基线 tpmC | 359 | 同上 |
| 已完成优化提升 | +50 / +14% | 表级执行锁阶段 |
| Kosthi 2024 决赛 tpmC | 8 万（赛后通道） | Kosthi README |
| RushDB 2025 决赛 tpmC | 3.2 万~16 万 | RushDB README + Kosthi README |
| 决赛 tpmC 上限（25 年） | 10 万~16 万 | Kosthi README |
| 团队目标 tpmC | 1500+ | 团队性能提升实施方案 §11 |
| 修订后预测 tpmC（P0 完成） | **2000~4000** | 本报告源码验证后预测 |
| 修订后预测 tpmC（P2 完成） | **5000~10000+** | 本报告源码验证后预测 |

## 0.3 三个最关键的行动项

### 🔥 第 1 优先（1 天内，改 3 行代码）

```cpp
// src/rmdb.cpp:41
#define MAX_CONN_LIMIT 256              // 原 8

// src/rmdb.cpp:50
static constexpr int kExplicitTxnAdmissionLimit = 16;  // 原 1

// src/test/performance_test/table_data/warehouse.csv 第2行末尾
// w_ytd: 3000.5 → 90001.5
```

加上 CMakeLists.txt 的 `-O3 -DNDEBUG -march=native -flto`，这 4 项改动预期带来 **+400%~500%** tpmC 提升。

### 🔥 第 2 优先（1 周内，修复致命缺陷）

修复 UPDATE 列自引用支持（`SET col = col + value`），否则官方决赛 SQL 解析失败，**性能测试 0 分**。

### 🔥 第 3 优先（2-3 周内，冲击高分）

P1 优化项：reentrant parser、后台刷脏页、IxCompare 特化、UPDATE 原地更新、后台 WAL flush、标量聚合专用路径。

---

# 第一部分：研究方法论与数据来源

## 1.1 研究范围

本报告整合了整个对话过程中的 5 轮研究产出：

| 轮次 | 研究内容 | 产出 |
|------|---------|------|
| 第 1 轮 | 开源项目检索 + 源码深度分析 | RUCBase 优化方案深度研究报告 v1.0 |
| 第 2 轮 | Kosthi 仓库 290 条 git 提交挖掘 | 获奖项目 Git 历史比赛经验 v1.0 |
| 第 3 轮 | 两份报告合并 | 优化方案与备赛经验最终汇报 v2.0 |
| 第 4 轮 | 团队上传文档（2026-rmdb-docs.zip）解析 | 参赛现状分析与优化方案 v3.0 |
| 第 5 轮 | 团队上传源码（2026-our-源码.zip）逐文件验证 | 源码级深度分析补充报告 v4.0 |

## 1.2 数据来源

### 1.2.1 历届获奖项目（外部参考）

| 项目 | 链接 | 价值 | 数据量 |
|------|------|------|--------|
| Kosthi/CSCC-DB-Rucbase-2024 | https://github.com/Kosthi/CSCC-DB-Rucbase-2024 | 2024 一等奖（2/325），8 万 tpmC | 290 commits, 17 branches, 全量源码 |
| RushDB-Lab/CSCC-DB-Rucbase-2025 | https://github.com/RushDB-Lab/CSCC-DB-Rucbase-2025 | 2025 一等奖（2/362），3.2 万~16 万 tpmC | 全量源码（1 次 initial commit） |
| ruc-deke/rucbase-lab | https://github.com/ruc-deke/rucbase-lab | 官方原版框架 | 全量源码 |
| Kosthi/TPCC-Tester | https://github.com/Kosthi/TPCC-Tester | TPC-C 测试脚本 | 全量源码 |
| Kosthi Issue#1 | https://github.com/Kosthi/CSCC-DB-Rucbase-2024/issues/1 | 优化思路讨论 | Kosthi 队长亲述 |

### 1.2.2 团队上传文档（内部资料）

- `2026-rmdb-docs.zip`（1.2MB）：包含 `docs/{official,dev,perf,problem,debug}-doc/` 五层文档体系，50+ 篇 md
- `2026-our-源码.zip`（1.5MB）：包含 `src/` 全量源码（排除 deps/ 和 CMakeFiles/）

### 1.2.3 官方赛规资料

- `task-11-performance.md`：性能测试题面与硬编码优化禁令
- `比赛交流群信息汇总-07-03.md`：明泰公告（赛规澄清）
- `决赛性能测试SQL示例.md`：官方决赛 SQL（使用 `col = col + value`）
- `数据一致性检验规则.md`：4 类一致性约束
- `虚拟机报告.md`：评测环境硬件（40 核 / 2 NUMA / AVX-512 / 内核 3.10）

## 1.3 研究方法

1. **开源项目逆向分析**：下载源码 → 逐文件阅读 → 提取优化技术 → 三维评级（性能潜力/实现风险/竞赛适用性）
2. **Git 历史挖掘**：`git clone --filter=blob:none` → `git log --all` → 按分支/时间/类型分类 → 还原开发轨迹
3. **文档体系解析**：解压 zip → 按 README 导航 → 逐目录阅读 → 交叉验证
4. **源码逐行验证**：解压源码 → 对照文档判断 → grep 关键模式 → 修正文档错误判断

---

# 第二部分：历届获奖项目深度分析

## 2.1 Kosthi 2024（保守路线代表）

### 2.1.1 基本信息

| 项 | 值 |
|----|-----|
| 团队 | DataDance（沈阳工业大学，吴奕民/张梦圆） |
| 成绩 | 2024 一等奖（2/325），决赛赛后通道 **8 万 tpmC** |
| 架构 | 2PL（严格两阶段锁）+ 间隙锁 + Crab Protocol |
| WAL | `#ifdef ENABLE_LOGGING` 编译期开关，`flush_log_to_disk()` 被注释 |
| 缓冲池 | 16 实例 BufferPool + ClockReplacer，256MB |
| 关键技术 | PageGuard RAII、RWLatch（std::shared_mutex）、谓词管理器、TPC-C UPDATE 跳过间隙锁检查 |

### 2.1.2 核心优化方案

| 文件 | 优化 | 原理 |
|------|------|------|
| `src/storage/page_guard.h/cpp` | PageGuard RAII + `noexcept` 移动 | 替代裸 pin/unpin，避免漏 unpin |
| `src/storage/rwlatch.h` | `RWLatch` 封装 `std::shared_mutex` | C++17 标准读写锁 |
| `src/storage/buffer_pool_instance.h/cpp` | 16 实例 BufferPool + `page_table_.reserve(20000)` | 分片降低锁竞争 |
| `src/common/config.h` | `BUFFER_POOL_SIZE = 65536` (256MB) | 装下 50 warehouse |
| `src/transaction/transaction_manager.cpp` | `#ifdef ENABLE_LOGGING` 包裹日志 | WAL 编译期可控 |
| `src/execution/predicate_manager.h` | 谓词预解析为左右边界 | 避免每次 scan 重复解析 WHERE |
| `src/execution/executor_update.h` | 注释掉 TPC-C UPDATE 间隙锁检查 | 基于"UPDATE 不改键"的事务特征 |
| `src/optimizer/planner.cpp` | 索引最长前缀匹配 + 等号优先 | 自动选择最优索引 |

### 2.1.3 关键代码片段

**WAL 编译期关闭**：

```cpp
void TransactionManager::commit(Transaction* txn, LogManager* log_manager) {
    // ... 释放锁 ...
#ifdef ENABLE_LOGGING  // 编译期开关
    auto* commit_log_record = new CommitLogRecord(txn->get_transaction_id());
    txn->set_prev_lsn(log_manager->add_log_to_buffer(commit_log_record));
    // log_manager->flush_log_to_disk();  // ← 被注释
    delete commit_log_record;
#endif
    txn->set_state(TransactionState::COMMITTED);
}
```

**TPC-C UPDATE 跳过间隙锁**：

```cpp
// TPCC 测试中 update 不会涉及键的变化，在 index scan
// 算子加了写间隙锁后就不用再检查了
// for (auto &[index_name, index]: tab_.indexes) {
//     ... isSafeInGap(...) ...
// }
```

## 2.2 RushDB 2025（激进路线代表）

### 2.2.1 基本信息

| 项 | 值 |
|----|-----|
| 团队 | RushDB（成都理工大学，明泰/胡鑫） |
| 成绩 | 2025 一等奖（2/362），README 公开 **32,820 txns/min** |
| 架构 | 双轨制（`*_finals.*` 决赛专用代码）+ phmap::btree_set 内存 B+树 + 解析器旁路 |
| 核心 | 利用"TPC-C 只测 tpmC 不验证数据持久化"的赛规特点 |

### 2.2.2 核心优化方案（多数不可借鉴）

| 文件 | 优化 | 可借鉴性 |
|------|------|---------|
| `src/rmdb_finals.cpp` | `#define NDEBUG` + `DBCahce::has_cache` 旁路 + `pthread_create` 替代线程池 | ❌ 旁路属硬编码 |
| `src/cahce/cache.h` | `switch(sql[0])` 首字符分派 INSERT/COMMIT/BEGIN | ❌ 绕过通用解析 |
| `src/index/ix_index_handle_finals.h` | `phmap::btree_set` 替代 B+树 + `IxCompare` 模板特化 | ⚠️ 替代不可，特化可 |
| `src/record/rm_file_handle_finals.h` | `unordered_set<char*>` 内存 record + `ban` 标志空转 | ❌ 明显作弊 |
| `src/execution/executor_index_scan_finals.h` | `exact_match_mode_` 全等值快速路径 | ✅ 通用优化可借鉴 |
| `src/execution/executor_update_finals.h` | `perform_in_place_update` 原地更新 | ✅ 通用优化可借鉴 |
| `src/execution/execution_scaler_group_finals.h` | `ScalerAggPlanExecutor` 标量聚合专用路径 | ✅ 通用优化可借鉴 |

### 2.2.3 关键代码片段

**DBCahce 旁路解析器**：

```cpp
inline bool DBCahce::has_cache(const char *sql, Context *ctx) const {
    switch (sql[0]) {
        case 'i': { do_insert_cache(sql, ctx); return true; }  // INSERT
        case 'c': { if (sql[1] == 'o') { do_commit_cache(ctx); return true; } }  // COMMIT
        case 'b': { do_begin_cache(ctx); return true; }  // BEGIN
        default: { return false; }
    }
}
```

**IxCompare 模板特化**：
```cpp
class IxCompare {
    bool single_int_ = false;       // 单列int快速路径
    bool all_int_ = false;          // 全int快速路径
    bool small_all_int_ = false;    // 2/3/4列int手动unroll
    int small_int_off_[4] = {0,0,0,0};
    
    inline bool operator()(const char *a, const char *b) const {
        if (single_int_) { /* 最快路径 */ }
        if (small_all_int_) {
            switch (small_int_cnt_) {
                case 2: { /* 手动unroll 2列 */ }
                case 3: { /* 手动unroll 3列 */ }
                case 4: { /* 手动unroll 4列 */ }
            }
        }
        // 通用路径
    }
};
```

## 2.3 两队对比

| 维度 | Kosthi 2024 | RushDB 2025 |
|------|------------|------------|
| 路线 | 2PL 保守 | 内存化激进 |
| 决赛 tpmC | 8 万 | 3.2 万~16 万 |
| 赛规风险 | 低（2024 较宽松） | 高（2025 已警告） |
| 工程化程度 | 中（野路子提交） | 高（双轨制架构） |
| 可复现性 | 中 | 低（依赖赛规漏洞） |
| 2026 适用性 | ⚠️ 部分可借鉴（2PL→MVCC 不兼容） | ❌ 核心方案不可借鉴 |

---

# 第三部分：获奖项目 Git 历史经验挖掘

## 3.1 Kosthi 仓库全景

| 指标 | 数值 |
|------|------|
| 总提交数 | 290（去重） |
| 分支数 | 17 |
| 时间跨度 | 2024-05-20 ~ 2025-08-24（约 15 个月） |
| 主开发期 | 2024-05-20 ~ 2024-08-30（约 100 天） |
| 月度峰值 | 2024-08（102 commits，决赛冲刺） |

## 3.2 分支结构揭示的开发模型

```
main (288 commits) ──────────────────────────────────── 主线
 ├─ Task1-StorageManagement (9)         ─┐
 ├─ Task2-QueryExecution (16)            │
 ├─ Task3-UniqueIndex (40)               │  初赛 11 个 Task 分支
 ├─ Task4-AggGroup (48)                  │  按"模块功能"切分
 ├─ Task5-IrrSubquery (64)               │
 ├─ Task6-SortMerge (67)                 │
 ├─ Task7-TxnControl (68)                │
 ├─ Task8-ConflictSerial (72)            │
 ├─ Task9-GapLock (97)                   │
 ├─ Task10-StaticCheckpointRecovery (91) │
 ├─ Task11-Performance (125)            ─┘
 ├─ Preliminary-Competition (116)    ──── 初赛合并分支
 ├─ MVCC-Performance (145)           ──── MVCC 探索分支（未最终采用）
 ├─ Final-TPCC-3K (210)              ──── 决赛 3K tpmC 里程碑
 ├─ Final-TPCC-3W (237)              ──── 决赛 3W tpmC 里程碑
 └─ Final-Competition (275)          ──── 决赛最终分支
```

**关键洞察**：
1. **分支命名即里程碑**：`Final-TPCC-3K` / `Final-TPCC-3W` 用 tpmC 数值作为目标
2. **MVCC 探索分支独立未合并**：尝试后放弃，是重要"反例"经验
3. **Task 难度递增**：Task1 仅 9 commits，Task9/Task11 超 100 commits

## 3.3 关键时间节点

| 日期 | 事件 | 阶段意义 |
|------|------|---------|
| 2024-05-20 | `feat: init rmdb 2024` | 项目启动 |
| 2024-05-20 | 1 天完成 Task1（disk_manager/lru/buffer_pool） | 初赛快速启动 |
| 2024-05-22 | 实现 B+树 | Task3 核心 |
| 2024-06-04 | **使用 Crab Protocol** | Task8 关键决策 |
| 2024-06-05 | **支持 wait-die 死锁预防** | Task8 关键决策 |
| 2024-06-29 | Preliminary-Competition 定格 | 初赛提交 |
| 2024-07-19 | `feat: mvcc structure` | **MVCC 探索启动（后放弃）** |
| 2024-08-04 | 单日 15 次 feat 试错间隙锁 | 决赛密集调试 |
| 2024-08-07 | 单日 13 次行锁 vs 表锁反复 | 锁策略试错 |
| 2024-08-10 | 4 个间隙锁并发死锁修复 | 稳定期 |
| 2024-08-13~17 | **5 天 25 次 perf 优化** | Final-Competition 冲刺 |
| 2024-08-30 | `fix: load阶段正常载入索引` | 赛后修复 |

## 3.4 决赛冲刺 5 天 25 次优化（核心经验）

```
2024-08-13 perf: 优化成 send 发送 tcp 数据            ← TCP发送优化
2024-08-13 perf: 试试不分片                            ← 缓冲池分片试验
2024-08-14 perf: 调整缓冲池参数                        ← 参数调优
2024-08-14 perf: 优化解析层，减少冗余函数调用与拷贝     ← 解析层优化
2024-08-14 feat: 缩小buffer                            ← 缓冲池缩小（从4G降下来）
2024-08-14 feat: 实现缓冲池负载均衡                    ← 负载均衡
2024-08-14 perf: 不用加锁来                            ← 减少锁
2024-08-15 perf: 解析层支持多线程和移除冗余代码         ← 多线程解析
2024-08-15 perf: 为每个客户端分配一个语法解析器         ← 解析器实例化
2024-08-15 perf: 减少解析层拷贝耗时                    ← 拷贝优化
2024-08-15 perf: 优化 Analyze::get_all_cols 的开销     ← Analyze优化
2024-08-16 feat: 日志异步刷盘和减少事务控制锁冲突       ← 异步WAL
2024-08-16 perf: 为哈希表预留空间                      ← reserve()
2024-08-16 perf: 优化查询计划生成和执行阶段，减少拷贝   ← 计划生成优化
2024-08-17 perf: 优化增删改查算子构造函数，减少拷贝扩容  ← 算子优化
2024-08-17 perf: 减少索引点查询的匹配谓词次数          ← 索引点查优化
2024-08-17 perf: 插入记录时提前解锁再拷贝              ← 提前解锁
2024-08-17 perf: 不并行创建 Join 执行器                ← 反思：并行不一定快
2024-08-17 perf: 为间隙锁表预留空间                    ← reserve()
2024-08-17 fix: b+树解决空树和 upper_bound 特例情况   ← 边缘case修复
```

## 3.5 关键教训（5 个反例 + 6 个正例）

### 3.5.1 反例（不要重蹈覆辙）

| 反例 | 表现 | 教训 |
|------|------|------|
| MVCC 探索 | 7/19 启动，4 天后 `god bless me!` 放弃 | 不要在决赛前 1 个月尝试 MVCC |
| 缓冲池 4G | 从 4G 回退到 2G 并分片 | 缓冲池不是越大越好 |
| 并行创建 Join | 次日回退"不并行创建" | 多线程不一定快，轻量任务反例 |
| 消除所有行锁 | 次日恢复，DELETE 需行锁 | 不要消除所有行锁 |
| 8/04 单日 15 次试错 | `啊啊啊` / `咋回事` / `funny` | 情绪化提交是正常现象 |

### 3.5.2 正例（一次定型未反复）

| 正例 | 原因 |
|------|------|
| Crab Protocol for B+树 | 教科书方案，无争议 |
| wait-die 死锁预防 | 比 wound-wait 更适合 TPC-C |
| 静态检查点 | 实现简单，对性能影响小 |
| PageGuard RAII | CMU BusTub 标准方案 |
| `#ifdef ENABLE_LOGGING` 编译期开关 | 比运行时开关更彻底 |
| TPC-C UPDATE 跳过间隙锁检查 | 基于 TPC-C 事务特征 |

## 3.6 高频踩坑 TOP 10

| 排名 | 踩坑点 | 解决方案 |
|------|--------|---------|
| 1 | 空表/空树处理 | 所有 scan 类操作开头加 `if (empty) return;` |
| 2 | 内存泄漏 | PageGuard RAII + valgrind |
| 3 | 死锁 | wait-die 策略 + 加锁顺序规范 |
| 4 | unpin 漏掉 | PageGuard RAII |
| 5 | 写锁重复解锁 | RAII 包装锁 |
| 6 | WAL 顺序 | 严格遵守 WAL 原则 |
| 7 | 间隙锁并发 | INSERT 加写间隙锁 |
| 8 | file handle 并发 | RmFileHandle 加 mutex |
| 9 | 谓词误删 | 谓词管理器保留所有 op |
| 10 | 聚合空值 | 聚合前判空 |

---

# 第四部分：团队现状全景诊断

## 4.1 项目基本信息

| 维度 | 现状 |
|------|------|
| 比赛 | 2026 全国大学生计算机系统能力大赛——数据库管理系统设计赛 |
| 赛题版本 | 2026 题目（task-01 ~ task-11） |
| 官方框架 | RMDB（基于 rucbase-lab 演进） |
| 团队规模 | **3 人团队**（从 task-05-three-person-split 等多人分工文档可见） |
| 当前阶段 | task-11 性能优化阶段（task-01 ~ task-10 全部完成） |
| 文档体系 | 完整的 `docs/{official,dev,perf,problem,debug}-doc/` 五层文档体系 |
| 测试框架 | 自建 `scripts/rmdb_testkit/` 完整测试套件 |
| 协作规范 | CLAUDE.md 明文规定"禁止直接复制参考代码"、"禁止未经允许 push" |

## 4.2 技术架构现状

### 4.2.1 模块实现概览

| 模块 | 实现状态 | 关键技术 |
|------|---------|---------|
| **storage** | ✅ 已优化 | DiskManager 用 `pread/pwrite`；BufferPoolManager **16 分片 CLOCK**（已从单全局锁重构） |
| **record** | ✅ 完整 | 行存 `[PageHdr \| Bitmap \| Slots]`，支持 MVCC 的 `TupleMeta {ts_, is_deleted_}` |
| **index** | ✅ 完整 | 多列复合键 B+树，叶子双向链表，`root_latch_` 保护（**无节点级 latch**） |
| **parser** | ✅ 完整 | flex/bison，**不支持 UPDATE SET col = col + value** |
| **analyze** | ✅ 完整 | 列解析、类型检查、别名、聚合、UNION、谓词/投影下推准备 |
| **optimizer** | ✅ 完整 | 谓词下推 + 投影下推 + 索引选择 + INLJ |
| **execution** | ✅ 完整 | 13 种火山模型算子（**无 exact_match_mode 快速路径**） |
| **transaction** | ✅ 完整 | **MVCC + SSI + 2PL 三套并发控制**，支持 SI/SER 隔离级别 |
| **recovery** | ✅ 完整 | WAL + ARIES + Group Commit（跳过 fdatasync）+ 静态检查点 |
| **system** | ✅ 完整 | DbMeta/TabMeta/ColMeta/IndexMeta + DDL + `RebuildAllIndexes()` |

### 4.2.2 关键技术决策（团队已做出的）

1. **缓冲池**：256MB / 65536 帧 / **16 分片** / CLOCK 替换
2. **磁盘 I/O**：`pread/pwrite`（已从 `lseek+read/write` 切换）
3. **执行锁**：表级执行锁（已从全局 `g_exec_latch` 切换），按 fd 排序加锁
4. **WAL**：Group Commit + `fdatasync`（**已跳过 fdatasync**，但仍每事务同步 `write()`）
5. **并发控制**：**MVCC + SSI** 为主，2PL 作为备选模式
6. **隔离级别**：支持 READ_COMMITTED / REPEATABLE_READ / SERIALIZABLE，官方要求 SI + SER
7. **MVCC**：UndoLog + 版本链 + Watermark GC（已尝试激进 GC 但回退到保守 GC）

## 4.3 当前性能基线

| 指标 | 数值 | 来源 |
|------|------|------|
| 原始基线 tpmC | 359 | 性能提升实施方案 §1 |
| 当前 AC tpmC | **409.67** | 同上（表级执行锁阶段） |
| 提升幅度 | +50 tpmC / +14% | 表级锁 + rollback 局部化 + 关闭 stdout |
| 内存占用 | rmdb-max-rss ≈ 2.09 GB | 同上 |
| 缓冲池 | 256MB（65536 帧） | `src/common/config.h:37` |
| 缓冲池分片 | 16 片，每片 4096 帧 | 已完成 |
| 目标 tpmC | 1500+ | 性能提升实施方案 §11 |

## 4.4 已完成清单

1. ✅ 压测支持关闭 `output.txt` 写文件
2. ✅ `g_exec_latch` → 表级执行锁
3. ✅ rollback 局部化到真实写集涉及表
4. ✅ 关闭 `client_handler` 热路径 stdout/debug 日志
5. ✅ Buffer Pool 单全局锁 → **分片锁（生产 16 片）** + `DiskManager` 改 `pread/pwrite`
6. ✅ AC（步骤 1~3 时）：`median tpmC = 409.666667`

## 4.5 NOT-DO 清单（17 条，团队已尝试但放弃）

| 编号 | 方案 | 放弃原因 |
|------|------|---------|
| 17 | make_one_rel 别名修复 | 引入回归 |
| 16 | planner 全量替换 | 兼容性问题 |
| 15 | 投影下推遍历表名修复 | 与表别名耦合紧密 |
| 14 | scan 节点输出排序修复 | 引入回归 |
| 13 | get_all_cols 别名匹配修复 | 引入回归 |
| 12 | 2PL 运行时模式 | TPC-C 高竞争下死锁率高 |
| 11 | 异步刷盘后台线程 | 线程切换开销 |
| 10 | 双缓冲 WAL 刷盘 | 复杂度收益有限 |
| 09 | MVCC 显式事务准入控制 | 16 线程下不如放开（**注：源码显示又启用了**） |
| 08 | MVCC 激进 GC Pruning | OJ 正确性测试失败 |
| 07 | MVCC 版本时间戳缓存 | commit atomicity race |
| 06 | Undo Record Buffer 释放 | use-after-free |
| 05 | 跳过 fdatasync | 不符合持久性语义（**注：源码显示已跳过**） |
| 04 | LRU → CLOCK | CLOCK 抗扫描污染更好（已替换） |
| 03 | Buffer Pool 扩容 1GB | 256MB 足够 |
| 02 | Buffer Pool 扩容 512MB | NUMA 开销 |
| 01 | Group Commit 首次尝试 | 实现有 bug，后重新实现成功 |

## 4.6 当前六大瓶颈（团队自己识别 + 源码验证修正）

| 编号 | 瓶颈 | 团队文档判断 | 源码验证 | 修正 |
|------|------|------------|---------|------|
| 1 | `client_handler` stdout 日志 | 已关闭 | ✅ 已关闭 | - |
| 2 | `buffer_mutex` 串行化 parser | 第一瓶颈 | ✅ 确认串行 | - |
| 3 | commit 同步 fsync | 第二瓶颈 | ⚠️ **已跳过 fdatasync**，仍同步 write | 修正：瓶颈变小 |
| 4 | BufferPoolManager 全局锁 | 已改分片 | ✅ 已改 | - |
| 5 | MVCC 可见性开销 | 待优化 | ✅ 确认 | - |
| 6 | 高 abort-rate | 待优化 | ✅ 确认 | - |
| **7** | **显式事务串行化** | **未提及** | **🔥🔥 致命瓶颈** | **新增：最大瓶颈** |
| **8** | **无编译优化** | **未提及** | **🔥🔥 默认 -O0** | **新增：第二瓶颈** |
| **9** | **UPDATE 不支持列自引用** | **未提及** | **🔥🔥 0 分风险** | **新增：致命缺陷** |

---

# 第五部分：源码级深度验证（12 项关键发现）

通过逐文件阅读团队 `2026-our-源码.zip` 源码，发现文档与实际代码之间存在多处差异。**有些是已优化但文档未更新，有些是已退化但文档仍乐观**。

## 5.1 发现 1：🔥🔥 显式事务被强制串行化（最严重）

**源码位置**：`src/rmdb.cpp:49-50`

```cpp
static constexpr bool kEnableAdmissionControl = true;
static constexpr int kExplicitTxnAdmissionLimit = 1;
```

**含义**：所有显式事务（`BEGIN...COMMIT` 块）**同时只允许 1 个执行**，其余事务在 `ReserveExplicitTxnSlot()` 中阻塞等待。

**影响**：
- TPC-C 的 5 种事务都是显式事务
- 16 线程并发压测时，实际只有 1 个事务在跑，其余 15 个排队
- **这是当前 tpmC 只有 409 的根本原因之一**

**与文档冲突**：`perf-doc/NOT-DO.md` 第 09 条记录"准入控制被移除，改为无限制并发"，但源码显示又重新启用了（可能是为了通过 AC 的临时方案）。

**修复方向**：`kExplicitTxnAdmissionLimit` 从 1 提升到 16，或 `kEnableAdmissionControl = false`。

## 5.2 发现 2：🔥 MAX_CONN_LIMIT = 8（不足）

**源码位置**：`src/rmdb.cpp:41`

```cpp
#define MAX_CONN_LIMIT 8
```

**影响**：官方 16 线程压测，backlog=8 可能导致连接拒绝。

**修复**：改为 `#define MAX_CONN_LIMIT 256`。

## 5.3 发现 3：✅ WAL 已跳过 fdatasync（半 Group Commit）

**源码位置**：`src/recovery/log_manager.cpp:22-24`

```cpp
// commit 只等待 WAL 写入内核页缓存，跳过每事务 fdatasync
static constexpr int kWalCoalesceDelayUs = 0;
static constexpr bool kWalFdatasyncOnFlush = false;
```

**含义**：
- `flush_up_to(lsn)` 仍每次 commit 同步调用，但内部跳过了 `fdatasync`
- 即每个 commit 仍做一次 `write()`（写入内核页缓存），但不强制落盘

**与文档冲突**：v3.0 报告说"仍同步刷盘"——**部分错误**。fdatasync 已跳过，但 `write()` 仍每事务同步。

**剩余优化空间**：后台线程批量 `write()`，预期再 +10%~30%。

## 5.4 发现 4：🔥🔥 UPDATE 完全不支持列自引用（确认致命缺陷）

**源码位置 1**：`src/parser/yacc.y:437-442`

```yacc
setClause:
        colName '=' value
    {
        $$ = std::make_shared<SetClause>($1, $3);
    }
    ;
```

**源码位置 2**：`src/parser/ast.h:302-308`

```cpp
struct SetClause : public TreeNode {
    std::string col_name;
    std::shared_ptr<Value> val;  // 只能是字面量
    SetClause(std::string col_name_, std::shared_ptr<Value> val_) :
            col_name(std::move(col_name_)), val(std::move(val_)) {}
};
```

**源码位置 3**：`src/common/common.h:115-118`

```cpp
struct SetClause {
    TabCol lhs; // 列
    Value rhs;  // 值（只能是字面量）
};
```

**源码位置 4**：`src/execution/executor_update.h:81-93`

```cpp
for (auto &set_clause : set_clauses_) {
    auto col = tab_.get_col(set_clause.lhs.col_name);
    Value val = set_clause.rhs;  // 直接取字面量，无表达式求值
    ...
}
```

**确认**：完全不支持 `UPDATE SET col = col + value`。而官方决赛 SQL 示例明确使用：

```sql
update warehouse set w_ytd=w_ytd+:h_amount where w_id=:w_id;
update district set d_ytd=d_ytd+:h_amount where d_w_id=:w_id and d_id=:d_id;
update customer set c_balance=:c_balance, c_delivery_cnt=c_delivery_cnt+1 where ...;
```

**后果**：官方性能测试时，这些 UPDATE 会解析失败 → 一致性检查必然失败 → **0 分**。

## 5.5 发现 5：🔥 测试数据未修复

**源码位置**：`src/test/performance_test/table_data/warehouse.csv` 第 2 行

```csv
1,JxMJvSF3vi,...,0.125,3000.5
```

**源码位置**：`src/test/performance_test/table_data/district.csv` 第 2-4 行

```csv
1,1,...,0.3125,30000.5,11
2,1,...,0.3125,30000.5,11
3,1,...,0.3125,30000.5,11
```

**确认**：`w_ytd=3000.5`，`SUM(d_ytd)=90001.5`，差异 -87001.0。**至今未修复**。

**修复**：将 `warehouse.csv` 的 `w_ytd` 从 `3000.5` 改为 `90001.5`。

## 5.6 发现 6：🔥🔥 没有编译优化选项

**源码位置**：`src/CMakeLists.txt`

```cmake
include_directories(${CMAKE_CURRENT_SOURCE_DIR})
add_subdirectory(analyze)
...
add_executable(rmdb rmdb.cpp)
target_link_libraries(rmdb parser execution readline pthread planner analyze)
```

**确认**：**完全没有** `-O2` / `-O3` / `-DNDEBUG` / `-march=native` / `-flto`。

**与文档冲突**：`CLAUDE.md` 第 118 行说"CMake 已配置 -O2 优化级别"——**实际没有**。

**影响**：默认 `-O0`（无优化），性能损失 30%~50%。

**修复**：CMakeLists.txt 加 `-O3 -DNDEBUG -march=native -flto`。

## 5.7 发现 7：🔥 buffer_mutex 仍在串行化 parser

**源码位置**：`src/rmdb.cpp:724, 736, 887`

```cpp
pthread_mutex_lock(buffer_mutex);
YY_BUFFER_STATE buf = yy_scan_string(data_recv);
if (yyparse() == 0) {
    if (ast::parse_tree != nullptr) {
        try {
            std::shared_ptr<Query> query = analyze->do_analyze(ast::parse_tree);
            yy_delete_buffer(buf);
            finish_analyze = true;
            pthread_mutex_unlock(buffer_mutex);
            // 后续 optimizer/portal/run 不在锁内
```

**确认**：`buffer_mutex` 保护 `yy_scan_string` + `yyparse` + `do_analyze`，所有线程的解析+语义分析串行。

## 5.8 发现 8：❌ 没有后台刷脏页线程

**源码位置**：`src/storage/buffer_pool_manager.cpp:55-68`

```cpp
void BufferPoolManager::update_page(Shard &shard, Page *page, PageId new_page_id, frame_id_t new_frame_id) {
    if (page->is_dirty()) {
        flush_log_before_page_write(page);  // 同步 WAL flush
        disk_manager_->write_page(...);     // 同步写磁盘
        page->is_dirty_ = false;
    }
    ...
}
```

**确认**：victim page 替换时，**同步** flush WAL + write_page，没有后台预刷。

## 5.9 发现 9：❌ 没有 PageGuard / RWLatch

**源码位置**：`src/storage/` 目录

```
src/storage/
├── CMakeLists.txt
├── buffer_pool_manager.cpp
├── buffer_pool_manager.h
├── disk_manager.cpp
├── disk_manager.h
└── page.h
```

**确认**：
- **没有** `page_guard.h` / `rwlatch.h`（Kosthi 2024 有）
- `Page` 类**没有**内置 `RWLatch`
- B+树只有 `std::mutex root_latch_`（`src/index/ix_index_handle.h:322`），没有节点级 latch
- 没有 Crab Protocol 实现

## 5.10 发现 10：❌ IxCompare 无模板特化，IndexScan 无 exact_match 快速路径

**源码位置**：`src/index/ix_index_handle.h:25-59`

```cpp
inline int ix_compare(const char* a, const char* b, ColType type, int col_len) {
    switch (type) {
        case TYPE_INT: { ... }
        case TYPE_FLOAT: { ... }
        case TYPE_STRING: return memcmp(a, b, col_len);
    }
}
```

**确认**：
- 通用逐列比较，**无** 2/3/4 列 int 手动 unroll 特化
- `IndexScanExecutor`（452 行）**无** `exact_match_mode_` 快速路径

## 5.11 发现 11：⚠️ UPDATE 没有原地更新优化

**源码位置**：`src/execution/executor_update.h:95-114, 278-302`

```cpp
// 总是计算 old_keys 和 new_keys
pending.old_keys.resize(tab_.indexes.size());
pending.new_keys.resize(tab_.indexes.size());
for (size_t index_i = 0; index_i < tab_.indexes.size(); ++index_i) {
    // 拷贝 old_keys 和 new_keys
}

// 索引列未变时跳过 delete+insert（已有）
for (size_t index_i = 0; i < tab_.indexes.size(); ++index_i) {
    if (memcmp(pending.old_keys[index_i].data(), pending.new_keys[index_i].data(), ...) == 0) {
        continue;  // ✅ 已有此优化
    }
    ix_handle->delete_entry(...);
}
```

**确认**：
- 已有"索引列未变跳过"优化 ✅
- 但**没有** `col_in_index` 提前判断——即使所有 SET 列都不在索引中，仍计算 old_keys/new_keys 并 memcmp

## 5.12 发现 12：✅ 已确认的正确实现

| 项 | 源码验证 | 状态 |
|----|---------|------|
| 16 分片 BufferPool + CLOCK | `buffer_pool_manager.h:66` `kDesiredShards = 16` | ✅ |
| `pread/pwrite` 替代 lseek | `disk_manager.cpp:35, 54` | ✅ |
| 表级执行锁 + fd 排序 | `rmdb.cpp:454-463` `AcquireExecutionLocks` | ✅ |
| rollback 局部化 | `rmdb.cpp:602` `CollectWriteSetTableFds` | ✅ |
| 关闭 stdout 日志 | `rmdb.cpp:45` `kEnableClientRequestTrace = false` | ✅ |
| `set output_file off` | `rmdb.cpp:668-675` | ✅ |
| MVCC + SSI 完整实现 | `transaction_manager.cpp` 1025 行 | ✅ |
| Group Commit 部分（跳过 fdatasync） | `log_manager.cpp:24` | ✅ |
| wait-die 死锁预防 | `lock_manager.cpp` | ✅ |
| 静态检查点 + ARIES 恢复 | `recovery/checkpoint_manager.h` + `log_recovery.cpp` | ✅ |
| WAL + page_lsn | `buffer_pool_manager.cpp:46` | ✅ |
| 索引恢复后 RebuildAllIndexes | `rmdb.cpp:1063-1065` | ✅ |

## 5.13 文档与源码差异对照表

| 项 | 文档说的 | 源码实际 | 差异 |
|----|---------|---------|------|
| 编译优化 | "CMake 已配置 -O2" (CLAUDE.md:118) | 无任何 -O 选项 | ❌ 文档错误 |
| 显式事务并发 | "改为无限制并发" (NOT-DO #09) | `kExplicitTxnAdmissionLimit = 1` | ❌ 文档过期 |
| WAL fsync | "仍同步刷盘" (v3.0 报告) | `kWalFdatasyncOnFlush = false` | ⚠️ 部分错误 |
| buffer_mutex | "仍是串行瓶颈" | 确认串行 | ✅ 准确 |
| PageGuard | 未提及 | 不存在 | ❌ 缺失 |
| IxCompare 特化 | 未提及 | 无特化 | ❌ 缺失 |
| exact_match_mode | 未提及 | 无快速路径 | ❌ 缺失 |
| UPDATE 原地更新 | 未提及 | 有索引列未变跳过，无 col_in_index 提前判断 | ⚠️ 部分实现 |
| 后台刷脏页 | "待做" | 确认无 | ✅ 准确 |
| UPDATE 列自引用 | "必须修复" | 确认不支持 | ✅ 准确 |
| 测试数据一致性 | "需修复" | 确认未修复 | ✅ 准确 |
| MAX_CONN_LIMIT | 未提及 | 8（不足） | ❌ 缺失 |

---

# 第六部分：团队 vs 历届获奖项目对比

## 6.1 架构路线对比

| 维度 | Kosthi 2024 | RushDB 2025 | 团队 2026 |
|------|------------|------------|-----------|
| **并发控制** | 2PL + 间隙锁 | MVCC（finals 旁路） | **MVCC + SSI**（按 2026 题面要求） |
| **隔离级别** | 可串行化（2PL） | - | SI + SER（MVCC 实现） |
| **WAL** | 编译期关（`flush_log_to_disk` 注释） | 全内存（无 WAL） | Group Commit + 跳过 fdatasync（仍同步 write） |
| **缓冲池** | 16 实例 + CLOCK，256MB | 全内存 | 16 分片 + CLOCK，256MB ✅ 一致 |
| **B+树并发** | Crab Protocol | phmap::btree_set（无并发） | `root_latch_`（无节点级 latch） |
| **死锁预防** | wait-die | - | wait-die ✅ 一致 |
| **PageGuard** | RAII 封装，noexcept 移动 | 不需要（全内存） | **不存在** |
| **TPC-C UPDATE 优化** | 跳过间隙锁检查 | 原地更新 | **无优化** |
| **解析器并行** | 每客户端独立解析器 | 旁路解析器 | **仍 buffer_mutex 串行** |
| **决赛冲刺** | 5 天 25 次 perf 优化 | 双轨制架构 | 尚未进入此阶段 |
| **当前 tpmC** | 8 万 | 3.2 万~16 万 | **409** |

## 6.2 关键差异分析

### 6.2.1 并发控制模型完全不同

**Kosthi 用 2PL，团队用 MVCC + SSI**——这是因为 2026 题面 task-09 明确要求 MVCC + SSI。

**影响**：
- 团队的 MVCC 实现复杂度远高于 Kosthi 的 2PL，但理论冲突率更低
- 团队的 SSI 检测有运行时开销，Kosthi 没有
- **不能直接套用 Kosthi 的"消除所有行锁"等 2PL 专属优化**

### 6.2.2 WAL 处理方式不同

**Kosthi 直接编译期关闭 WAL**（2024 决赛不测崩溃恢复）。
**团队必须保留 WAL 并支持崩溃恢复**（2026 题面明确要求）。

**影响**：
- 不能照搬 Kosthi 的"编译期关 WAL"
- 但可以借鉴其 Group Commit 思路，团队已经在做（已跳过 fdatasync）
- 团队的 WAL 优化空间更小，需要更精细

### 6.2.3 显式事务串行化是团队独有

**Kosthi 和 RushDB 都没有显式事务串行化**，团队却启用了 `kExplicitTxnAdmissionLimit = 1`。

**这是团队当前最大的性能黑洞**——16 线程压测被强制串行化为 1。

### 6.2.4 编译优化差距

**Kosthi 和 RushDB 都用了 -O3**，团队默认 -O0。

**这是团队第二大的性能黑洞**——从 -O0 到 -O3 至少 +30%~50%。

## 6.3 可直接借鉴的 Kosthi 经验

| Kosthi 优化 | 团队是否已做 | 建议优先级 |
|------------|------------|----------|
| 16 分片 BufferPool + CLOCK | ✅ 已做 | - |
| `pread/pwrite` 替代 `lseek+read/write` | ✅ 已做 | - |
| 表级执行锁 + fd 排序加锁 | ✅ 已做 | - |
| rollback 局部化到真实写集 | ✅ 已做 | - |
| 关闭 stdout/debug 日志 | ✅ 已做 | - |
| 关闭 `output.txt` 写入 | ✅ 已做 | - |
| **为每个客户端分配独立解析器**（去 `buffer_mutex`） | ❌ 待做 | **P0** |
| **Group Commit + fdatasync** | ⚠️ 部分完成（已跳过 fdatasync，仍同步 write） | **P1** |
| **缩小执行锁覆盖范围** | ❌ 待做 | **P0** |
| **后台 log flush 线程** | ❌ 待做 | P1 |
| **后台刷脏页** | ❌ 待做 | P1 |
| **TPC-C UPDATE 跳过间隙锁检查** | ❌ 待做 | P1（需验证 SSI 下安全） |
| **谓词管理器预解析 WHERE** | ⚠️ 部分有 | P2 |
| **`reserve()` 预分配哈希表** | ❓ 未明确 | P2 |
| **`noexcept` 移动构造** | ❓ 未明确 | P2 |
| **`static_cast` 替代 `dynamic_pointer_cast`** | ❓ 未明确 | P2 |
| **TPC-C 事务级优化** | ❌ 待做 | P2 |
| **页级 latch**（heap/index/page） | ❌ 待做 | P3 |
| **NUMA 感知** | ❌ 待做 | P3 |

---

# 第七部分：可借鉴与不可借鉴清单

## 7.1 ❌ 不可借鉴（赛规禁止或架构不兼容）

| 方案 | 不可借鉴原因 |
|------|------------|
| RushDB finals 双轨制架构 | 2026 题面禁止"绕过通用流程的硬编码优化" |
| RushDB `phmap::btree_set` 替代 B+树 | 决赛要验证 B+树结构和崩溃恢复 |
| RushDB `unordered_set<char*>` 内存 record | 决赛要验证数据持久化 |
| RushDB `ban` 标志空转写操作 | 明显作弊，取消资格 |
| RushDB `DBCahce::has_cache` 首字符分派 | 属于"绕过通用解析"的硬编码 |
| Kosthi `#ifdef ENABLE_LOGGING` 编译期关 WAL | 2026 决赛要测崩溃恢复 |
| Kosthi 注释 `flush_log_to_disk()` | 同上 |
| Kosthi 消除所有行锁 | 团队用 MVCC，无行锁概念；SSI 下不能简化 |
| Kosthi 关闭唯一性检查 | 决赛要验证数据一致性 |
| MVCC 快照隔离重写 | 团队已经实现 MVCC + SSI，无需重写 |
| 团队 NOT-DO #02/03：Buffer Pool 扩容 512MB/1GB | 已尝试两次都回退 |
| 团队 NOT-DO #06：Undo Record Buffer 提前释放 | use-after-free |
| 团队 NOT-DO #07：MVCC 版本时间戳缓存 | commit atomicity race |
| 团队 NOT-DO #08：MVCC 激进 GC Pruning | OJ 正确性测试失败 |
| 团队 NOT-DO #11：异步刷盘后台线程（旧方案） | 被 Group Commit 替代 |
| 团队 NOT-DO #12：2PL 运行时模式 | TPC-C 高竞争下死锁率高 |

## 7.2 ✅ 可借鉴（通用优化，赛规允许）

| 方案 | 来源 | 预期收益 | 团队现状 |
|------|------|---------|---------|
| **放开显式事务串行化** | 团队独有发现 | **+400%~900%** | ❌ 待做（最高优先） |
| **编译优化** `-O3 -DNDEBUG -march=native -flto` | 通用 | **+30%~50%** | ❌ 待做（默认 -O0） |
| **修复 UPDATE 列自引用** | 官方 SQL 要求 | 一致性可过（避免 0 分） | ❌ 待做（致命缺陷） |
| 为每个客户端分配独立解析器 | Kosthi | +5%~15% | ❌ 待做 |
| Group Commit + 后台 flush 线程 | Kosthi + 团队方案 | +10%~30%（已跳过 fdatasync） | ⚠️ 部分完成 |
| 缩小执行锁覆盖范围 | 团队方案 | +10%~25% | ❌ 待做 |
| 后台刷脏页 | 团队方案 | +8%~25% | ❌ 待做 |
| `IxCompare` 模板特化 | RushDB | +5%~10% | ❌ 待做 |
| `exact_match_mode_` 全等值快速路径 | RushDB | +10%~20% | ❌ 待做 |
| `perform_in_place_update` 原地更新 | RushDB | +10%~15% | ❌ 待做（部分有） |
| `ScalerAggPlanExecutor` 标量聚合专用路径 | RushDB | +5%~10% | ❌ 待做 |
| `#define NDEBUG` 关 assert | RushDB | +3%~5% | ❓ 未明确 |
| `reserve()` 预分配哈希表 | Kosthi + RushDB | +3%~8% | ❓ 未明确 |
| `noexcept` 移动构造 | Kosthi | +2%~5% | ❓ 未明确 |
| `static_cast` 替代 `dynamic_pointer_cast` | RushDB | +3%~8% | ❓ 未明确 |
| TPC-C UPDATE 跳过 SSI 检查（需验证） | Kosthi | +5%~10% | ❌ 待做 |
| 谓词管理器预解析 WHERE | Kosthi | +5%~10% | ⚠️ 部分有 |
| TPC-C 事务级优化（Delivery/OrderStatus） | Kosthi | +10%~20% | ❌ 待做 |
| `data_send_is_full()` 提前终止 SELECT | RushDB | +3%~5% | ❓ 未明确 |
| 页级 latch（heap/index/page） | Kosthi + 团队方案 | +20%~40% | ❌ 待做（P3） |
| NUMA 感知（线程绑定 + 内存绑定） | 团队虚拟机报告 | +10%~20% | ❌ 待做 |
| AVX-512 加速哈希/比较 | 团队虚拟机报告 | +5%~15% | ❌ 待做 |
| `madvise(MADV_HUGEPAGE)` 透明大页 | 团队虚拟机报告 | +5%~10% | ❌ 待做 |

## 7.3 ⚠️ 需要谨慎评估的方案

| 方案 | 风险点 |
|------|--------|
| TPC-C UPDATE 跳过 SSI 检查 | 团队用 SSI 不用间隙锁，rw-dependency 检查能否跳过需验证 |
| `pthread_create` 替代线程池 | 16 连接下线程池开销可忽略 |
| Buffer Pool 扩容 | 团队已尝试两次都回退 |
| MVCC 激进 GC | 团队已尝试失败 |
| MVCC 版本时间戳缓存 | 团队已尝试失败 |

---

# 第八部分：优化方案全集（40+ 条）

## 8.1 按优先级排序的完整清单

### 🔥🔥 P0-0：放开显式事务串行化（最高优先级）

| 项 | 详情 |
|----|------|
| **文件** | `src/rmdb.cpp:49-50` |
| **当前** | `kEnableAdmissionControl = true; kExplicitTxnAdmissionLimit = 1` |
| **修改为** | `kEnableAdmissionControl = false` 或 `kExplicitTxnAdmissionLimit = 16` |
| **预期收益** | **+400%~900%**（从串行 1 到并行 8~16） |
| **风险** | 高（可能暴露 MVCC+SSI 并发 bug） |
| **验证** | 先跑 `pre_submit_check.sh` 完整正确性检查 |

### 🔥🔥 P0-1：编译优化（最高性价比）

| 项 | 详情 |
|----|------|
| **文件** | 仓库根目录 `CMakeLists.txt` 或 `src/CMakeLists.txt` |
| **添加** | `set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native -flto")` + `set(CMAKE_BUILD_TYPE Release)` |
| **预期收益** | **+30%~50%**（从 -O0 到 -O3） |
| **风险** | 低 |

### 🔥🔥 P0-2：修复 UPDATE 列自引用（最紧急）

| 项 | 详情 |
|----|------|
| **文件** | `src/parser/yacc.y` + `src/parser/ast.h` + `src/common/common.h` + `src/analyze/analyze.cpp` + `src/execution/executor_update.h` |
| **当前** | `setClause: colName '=' value`（只支持字面量） |
| **修改为** | 支持 `colName '=' colName '+' value` 和 `colName '=' colName '-' value` |
| **预期收益** | 一致性可过（避免 0 分） |
| **风险** | 中（4 层修改，需完整回归测试） |
| **不修复后果** | 官方决赛 SQL 解析失败，**性能测试 0 分** |

### 🔥 P0-3：修复测试数据

| 项 | 详情 |
|----|------|
| **文件** | `src/test/performance_test/table_data/warehouse.csv` 第 2 行 |
| **当前** | `w_ytd = 3000.5` |
| **修改为** | `w_ytd = 90001.5` |
| **预期收益** | 本地 benchmark 可验证 |
| **风险** | 低 |

### 🔥 P0-4：提升 MAX_CONN_LIMIT

| 项 | 详情 |
|----|------|
| **文件** | `src/rmdb.cpp:41` |
| **当前** | `#define MAX_CONN_LIMIT 8` |
| **修改为** | `#define MAX_CONN_LIMIT 256` |
| **预期收益** | 避免 16 线程压测时连接拒绝 |
| **风险** | 低 |

### 🔥 P0-5：缩小 buffer_mutex 范围

| 项 | 详情 |
|----|------|
| **文件** | `src/rmdb.cpp:724-736` |
| **当前** | `buffer_mutex` 保护 `yy_scan_string + yyparse + do_analyze` |
| **修改为** | 只保护 `yyparse()`，`do_analyze` 移出锁外 |
| **预期收益** | +3%~8% |
| **风险** | 低 |

### P1-1：reentrant parser 改造

| 项 | 详情 |
|----|------|
| **文件** | `src/parser/yacc.y` + `src/parser/ast.h` + `src/rmdb.cpp` |
| **改动** | `%define api.pure full` + `thread_local parse_tree` + 每客户端独立 scanner |
| **预期收益** | +5%~15% |
| **风险** | 中 |

### P1-2：后台刷脏页线程

| 项 | 详情 |
|----|------|
| **文件** | `src/storage/buffer_pool_manager.h/cpp` |
| **改动** | 新增 `bg_flush_thread_`，定期扫描脏页预刷（只刷 `page_lsn <= persist_lsn`） |
| **预期收益** | +8%~25% |
| **风险** | 中 |

### P1-3：IxCompare 模板特化 + exact_match_mode

| 项 | 详情 |
|----|------|
| **文件** | `src/index/ix_index_handle.h` + `src/execution/executor_index_scan.h` |
| **改动** | 新增 IxCompare 类（2/3/4 列 int 手动 unroll）+ `exact_match_mode_` 全等值走 `find_entry` |
| **预期收益** | +10%~20% |
| **风险** | 低 |

### P1-4：UPDATE 原地更新优化

| 项 | 详情 |
|----|------|
| **文件** | `src/execution/executor_update.h` |
| **改动** | 构造时检查 `set_clauses` 是否涉及索引列，不涉及时 `perform_in_place_update` |
| **预期收益** | +10%~15% |
| **风险** | 低 |

### P1-5：后台 WAL flush 线程

| 项 | 详情 |
|----|------|
| **文件** | `src/recovery/log_manager.h/cpp` |
| **改动** | 新增 `durable_lsn_` + 后台 flush 线程 + commit 等待 `durable_lsn >= my_lsn` |
| **预期收益** | +10%~30% |
| **风险** | 高（崩溃恢复语义） |

### P1-6：ScalerAggPlanExecutor 标量聚合专用路径

| 项 | 详情 |
|----|------|
| **文件** | `src/optimizer/plan.h` + `src/execution/execution_scaler_group.h`（新增） |
| **改动** | 识别无 GROUP BY 的纯聚合，生成 `T_ScalerAgg` Plan，直接遍历累加 |
| **预期收益** | +5%~10% |
| **风险** | 低 |

### P1-7：编译微优化

| 项 | 详情 |
|----|------|
| **改动** | `#define NDEBUG` + `reserve()` 预分配 + `noexcept` 移动 + `static_cast` 替代 `dynamic_pointer_cast` |
| **预期收益** | +5%~15% |
| **风险** | 低 |

### P2-1：PageGuard + RWLatch + 页级 latch

| 项 | 详情 |
|----|------|
| **新增文件** | `src/storage/rwlatch.h` + `src/storage/page_guard.h` |
| **改动** | Page 加 `RWLatch`，B+树实现 Crab Protocol |
| **预期收益** | +20%~40% |
| **风险** | 高 |

### P2-2：NUMA 感知优化

| 项 | 详情 |
|----|------|
| **改动** | `pthread_setaffinity` 绑定 16 工作线程到 node0 + `numa_alloc_onnode` 缓冲池分片 |
| **预期收益** | +10%~20% |
| **风险** | 中 |

### P2-3：AVX-512 加速

| 项 | 详情 |
|----|------|
| **改动** | `ix_compare` 用 `_mm512_cmp_epi32_mask` + 哈希用 `_mm512_crc32_u64` |
| **预期收益** | +5%~15% |
| **风险** | 低 |

### P2-4：透明大页

| 项 | 详情 |
|----|------|
| **改动** | 对缓冲池内存 `madvise(MADV_HUGEPAGE)` |
| **预期收益** | +5%~10% |
| **风险** | 低 |

## 8.2 按模块分类的完整清单

### 8.2.1 存储引擎层

| 优化方案 | 性能潜力 | 实现风险 | 竞赛适用性 | 来源 |
|---------|---------|---------|-----------|------|
| 用 `phmap::btree_set` 替代手写 B+树 | 高 | 中 | ❌ 决赛要验证 | RushDB |
| `unordered_set<char*>` 内存 record | 高 | 高 | ❌ 决赛要验证 | RushDB |
| `ban` 标志空转 | 高 | 极高 | ❌ 作弊 | RushDB |
| `IxCompare` 模板特化 | 中 | 低 | ✅ | RushDB |
| `exact_match_mode_` 全等值快速路径 | 高 | 低 | ✅ | RushDB |
| PageGuard RAII | 中 | 低 | ✅ | Kosthi |
| RWLatch 替代 pthread_rwlock | 中 | 低 | ✅ | Kosthi |
| 16 实例 BufferPool 分片 | 高 | 中 | ✅ | Kosthi（团队已做） |
| 256MB 装下 50 warehouse | 高 | 低 | ✅ | Kosthi（团队已做） |
| LSM-tree 顺序写 | 中 | 高 | ⚠️ | Issue#1 |
| 自定义内存池 | 中 | 低 | ✅ | RushDB |

### 8.2.2 事务与锁管理层

| 优化方案 | 性能潜力 | 实现风险 | 竞赛适用性 | 来源 |
|---------|---------|---------|-----------|------|
| `#ifdef ENABLE_LOGGING` 编译期关 WAL | 高 | 高 | ❌ 决赛测崩溃恢复 | Kosthi |
| 注释 `flush_log_to_disk()` | 高 | 高 | ❌ | Kosthi |
| 关闭唯一性检查 | 中 | 高 | ❌ 决赛验证数据 | RushDB |
| 注释 IxScan 读锁 | 中 | 高 | ❌ | RushDB |
| TPC-C UPDATE 跳过间隙锁检查 | 高 | 低 | ✅ | Kosthi |
| wait-die 死锁预防 | 中 | 低 | ✅ | Kosthi（团队已做） |
| MVCC 快照隔离重写 | 高 | 高 | ❌ 团队已有 | Issue#1 |
| 锁优先级劫持 | 中 | 高 | ⚠️ | 你方已知 |
| 批量锁释放 | 中 | 低 | ✅ | 你方已知 |
| 消除间隙锁 | 中 | 高 | ❌ | 你方已知 |

### 8.2.3 SQL 解析与查询优化层

| 优化方案 | 性能潜力 | 实现风险 | 竞赛适用性 | 来源 |
|---------|---------|---------|-----------|------|
| `DBCahce::has_cache` 首字符分派 | 高 | 中 | ❌ 硬编码 | RushDB |
| 手写解析替代 `std::stoi` | 中 | 低 | ✅ | RushDB |
| `static_cast` 替代 `dynamic_pointer_cast` | 中 | 低 | ✅ | RushDB |
| `constexpr` 数组替代 map | 低 | 低 | ✅ | RushDB |
| 索引最长前缀匹配 + 等号优先 | 中 | 低 | ✅ | Kosthi |
| 谓词管理器预解析 WHERE | 中 | 低 | ✅ | Kosthi |
| `ScalerAggPlanExecutor` 标量聚合 | 中 | 低 | ✅ | RushDB |
| `MergeJoinExecutor` 索引归并连接 | 中 | 低 | ✅ | RushDB |
| `data_send_is_full()` 提前终止 | 中 | 低 | ✅ | RushDB |
| 硬编码 TPC-C 5 种事务执行路径 | 高 | 中 | ❌ 硬编码 | 你方已知 |

### 8.2.4 执行层算子优化

| 优化方案 | 性能潜力 | 实现风险 | 竞赛适用性 | 来源 |
|---------|---------|---------|-----------|------|
| `perform_in_place_update` 原地更新 | 高 | 低 | ✅ | RushDB |
| `col_in_index` 提前判断 | 高 | 低 | ✅ | RushDB |
| `memory_pool_manager_->allocate` | 中 | 低 | ✅ | RushDB |
| `reserve()` 预分配 | 低 | 低 | ✅ | 两队 |
| `memcpy` 替代 `reinterpret_cast` | 低 | 低 | ✅ | RushDB |
| `noexcept` 移动构造 | 低 | 低 | ✅ | Kosthi |
| `find_entry` 一次定位 | 高 | 低 | ✅ | RushDB |
| `update_bounds` 内联边界计算 | 低 | 低 | ✅ | RushDB |

### 8.2.5 系统与 IO 层

| 优化方案 | 性能潜力 | 实现风险 | 竞赛适用性 | 来源 |
|---------|---------|---------|-----------|------|
| `#define NDEBUG` 关 assert | 中 | 低 | ✅ | RushDB |
| `pthread_create` 替代线程池 | 中 | 低 | ✅ | RushDB |
| `io_enabled_=false` 关 output.txt | 中 | 低 | ✅ | RushDB（团队已做） |
| `MAX_CONN_LIMIT 256` | 低 | 低 | ✅ | RushDB |
| `SO_REUSEADDR` 端口复用 | 低 | 低 | ✅ | RushDB |
| `setjmp/jmpbuf` 异常恢复 | 低 | 中 | ✅ | RushDB |
| NUMA 内存绑定 | 中 | 中 | ✅ | 团队虚拟机报告 |
| Cache Line 对齐 | 中 | 中 | ✅ | 团队虚拟机报告 |

---

# 第九部分：源码级实施指南（精确到行）

## 9.1 立即行动（第 1 天，3 项 1 行改动）

### 9.1.1 放开显式事务串行化

**文件**：`src/rmdb.cpp:49-50`

**当前**：
```cpp
static constexpr bool kEnableAdmissionControl = true;
static constexpr int kExplicitTxnAdmissionLimit = 1;
```

**修改为**：
```cpp
static constexpr bool kEnableAdmissionControl = false;  // 先完全关闭
static constexpr int kExplicitTxnAdmissionLimit = 16;   // 或保留开关但提升到 16
```

**验证步骤**：
1. 先 `kEnableAdmissionControl = false`，跑 `pre_submit_check.sh` 完整正确性检查
2. 如果正确性 OK，跑 `run_bench.sh --large --warmup 10 --measure 60 -r 3` 对比 tpmC
3. 如果正确性失败，记录 abort 原因，针对性修复 SSI/MVCC 并发 bug
4. 如果 tpmC 提升 < 2x，说明还有其他瓶颈；如果 > 5x，说明串行化是主因

### 9.1.2 提升 MAX_CONN_LIMIT

**文件**：`src/rmdb.cpp:41`

**当前**：`#define MAX_CONN_LIMIT 8`

**修改为**：`#define MAX_CONN_LIMIT 256`

### 9.1.3 修复测试数据

**文件**：`src/test/performance_test/table_data/warehouse.csv` 第 2 行

**当前**：`1,JxMJvSF3vi,...,0.125,3000.5`

**修改为**：`1,JxMJvSF3vi,...,0.125,90001.5`

### 9.1.4 开启编译优化

**文件**：仓库根目录 `CMakeLists.txt`（在 `project()` 之后添加）

```cmake
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native -flto")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "-flto")
```

**或在 `src/CMakeLists.txt` 末尾添加**：
```cmake
target_compile_options(rmdb PRIVATE -O3 -DNDEBUG -march=native -flto)
target_link_options(rmdb PRIVATE -flto)
```

## 9.2 修复 UPDATE 列自引用（第 2-3 天）

### 9.2.1 Parser 层

**文件 1**：`src/parser/yacc.y:437-442`

**当前**：
```yacc
setClause:
        colName '=' value
    {
        $$ = std::make_shared<SetClause>($1, $3);
    }
    ;
```

**修改为**：
```yacc
setClause:
        colName '=' value
    {
        $$ = std::make_shared<SetClause>($1, $3);
    }
    |   colName '=' colName '+' value
    {
        auto expr = std::make_shared<BinaryExpr>($3, SvCompOp::SV_OP_ADD, $5);
        $$ = std::make_shared<SetClause>($1, expr);
    }
    |   colName '=' colName '-' value
    {
        auto expr = std::make_shared<BinaryExpr>($3, SvCompOp::SV_OP_SUB, $5);
        $$ = std::make_shared<SetClause>($1, expr);
    }
    ;
```

### 9.2.2 AST 层

**文件 2**：`src/parser/ast.h:302-308`

**修改为**：
```cpp
struct SetClause : public TreeNode {
    std::string col_name;
    std::shared_ptr<Value> val;  // 简单字面量（向后兼容）
    std::shared_ptr<BinaryExpr> expr;  // 列自引用表达式（新增）
    bool is_expr = false;  // 新增标志
    
    SetClause(std::string col_name_, std::shared_ptr<Value> val_) :
            col_name(std::move(col_name_)), val(std::move(val_)), is_expr(false) {}
    SetClause(std::string col_name_, std::shared_ptr<BinaryExpr> expr_) :
            col_name(std::move(col_name_)), expr(std::move(expr_)), is_expr(true) {}
};
```

### 9.2.3 Common 层

**文件 3**：`src/common/common.h:115-118`

**修改为**：
```cpp
struct SetClause {
    TabCol lhs;
    Value rhs;  // 简单字面量
    bool is_expr = false;  // 是否为列自引用表达式
    TabCol rhs_col;  // 表达式中的列引用
    enum ExprOp { OP_NONE, OP_ADD, OP_SUB } expr_op = OP_NONE;
    Value expr_rhs;  // 表达式中的右值
};
```

### 9.2.4 Analyze 层

**文件 4**：`src/analyze/analyze.cpp:200-220`

**修改为**：
```cpp
for (auto &sv_set_clause : x->set_clauses) {
    SetClause set_clause;
    set_clause.lhs = {.tab_name = x->tab_name, .col_name = sv_set_clause->col_name};
    auto col = tab.get_col(sv_set_clause->col_name);
    
    if (sv_set_clause->is_expr) {
        set_clause.is_expr = true;
        set_clause.rhs_col = {.tab_name = x->tab_name, .col_name = sv_set_clause->expr->lhs->col_name};
        set_clause.expr_op = (sv_set_clause->expr->op == SvCompOp::SV_OP_ADD) 
                             ? SetClause::OP_ADD : SetClause::OP_SUB;
        set_clause.expr_rhs = convert_sv_value(sv_set_clause->expr->rhs);
    } else {
        set_clause.rhs = convert_sv_value(sv_set_clause->val);
        // 原有类型检查...
    }
    query->set_clauses.push_back(std::move(set_clause));
}
```

### 9.2.5 Executor 层

**文件 5**：`src/execution/executor_update.h:81-93`

**修改为**：
```cpp
for (auto &set_clause : set_clauses_) {
    auto col = tab_.get_col(set_clause.lhs.col_name);
    Value val;
    
    if (set_clause.is_expr) {
        // 列自引用：读当前列值，计算新值
        auto rhs_col = tab_.get_col(set_clause.rhs_col.col_name);
        char *cur_data = pending.old_rec->data + rhs_col->offset;
        
        if (col->type == TYPE_INT) {
            int cur_val = *reinterpret_cast<int*>(cur_data);
            int delta = set_clause.expr_rhs.int_val;
            int new_val = (set_clause.expr_op == SetClause::OP_ADD) 
                          ? cur_val + delta : cur_val - delta;
            val.set_int(new_val);
        } else if (col->type == TYPE_FLOAT) {
            float cur_val = *reinterpret_cast<float*>(cur_data);
            float delta = set_clause.expr_rhs.float_val;
            float new_val = (set_clause.expr_op == SetClause::OP_ADD) 
                            ? cur_val + delta : cur_val - delta;
            val.set_float(new_val);
        } else {
            throw IncompatibleTypeError("column self-reference only supports INT/FLOAT");
        }
    } else {
        val = set_clause.rhs;
    }
    
    if (col->type != val.type) {
        throw IncompatibleTypeError(...);
    }
    val.init_raw(col->len);
    memcpy(pending.new_rec->data + col->offset, val.raw->data, col->len);
}
```

**MVCC 注意**：表达式中的"读当前列值"使用 `pending.old_rec`（已通过 MVCC 可见性判断的版本），因此**天然原子**——读和写在同一个 X 锁/版本链保护下完成，不会丢失更新。

**验证**：
```bash
# 单线程
create table t(id int, val int);
insert into t values(1, 100);
update t set val = val + 50 where id = 1;
select * from t;  -- 期望: 1, 150
update t set val = val - 30 where id = 1;
select * from t;  -- 期望: 1, 120

# 多线程（验证无丢失更新）
# 跑 8 线程 400 次 update t set val = val + 1 where id = 1
# 期望最终 val = 500
```

## 9.3 P0 收尾（第 4-7 天）

### 9.3.1 缩小 buffer_mutex 范围

**文件**：`src/rmdb.cpp:724-736`

**当前**：
```cpp
pthread_mutex_lock(buffer_mutex);
YY_BUFFER_STATE buf = yy_scan_string(data_recv);
if (yyparse() == 0) {
    if (ast::parse_tree != nullptr) {
        try {
            std::shared_ptr<Query> query = analyze->do_analyze(ast::parse_tree);
            yy_delete_buffer(buf);
            finish_analyze = true;
            pthread_mutex_unlock(buffer_mutex);
```

**修改为**（do_analyze 移出锁外）：
```cpp
pthread_mutex_lock(buffer_mutex);
YY_BUFFER_STATE buf = yy_scan_string(data_recv);
std::shared_ptr<ast::TreeNode> local_parse_tree = nullptr;
if (yyparse() == 0) {
    local_parse_tree = ast::parse_tree;
    ast::parse_tree = nullptr;
}
yy_delete_buffer(buf);
pthread_mutex_unlock(buffer_mutex);  // 立即释放

if (local_parse_tree != nullptr) {
    try {
        std::shared_ptr<Query> query = analyze->do_analyze(local_parse_tree);
        // optimizer + portal + run
```

### 9.3.2 reentrant parser 改造（长期方案）

**文件**：`src/parser/yacc.y` 头部添加：
```yacc
%define api.pure full
%param { yyscan_t scanner }
```

**文件**：`src/parser/ast.h:525` 改为：
```cpp
// extern std::shared_ptr<ast::TreeNode> parse_tree;  // 删除全局变量
// 改为通过 yyparse 参数返回
```

**文件**：`src/rmdb.cpp` 每个 client_handler 创建独立 scanner：
```cpp
yyscan_t scanner;
yylex_init(&scanner);
// 连接生命周期内复用 scanner
// 连接关闭时 yylex_destroy(scanner);
```

## 9.4 P1 实施指南（第 8-21 天）

### 9.4.1 后台刷脏页线程

**文件**：`src/storage/buffer_pool_manager.h` 新增

```cpp
class BufferPoolManager {
    std::thread bg_flush_thread_;
    std::atomic<bool> bg_flush_running_{true};
    std::condition_variable bg_flush_cv_;
    std::mutex bg_flush_mutex_;
    
    void bg_flush_loop() {
        while (bg_flush_running_) {
            std::unique_lock<std::mutex> lk(bg_flush_mutex_);
            bg_flush_cv_.wait_for(lk, std::chrono::milliseconds(100), 
                                   [this] { return !bg_flush_running_; });
            for (auto &shard : shards_) {
                std::lock_guard<std::mutex> sl(shard.latch_);
                // 扫描 page_table，找 is_dirty_ 且 page_lsn <= persist_lsn 的页
                // 批量 write_page（不调 flush_log_before_page_write，后台不阻塞 commit）
            }
        }
    }
    
public:
    BufferPoolManager(...) {
        bg_flush_thread_ = std::thread(&BufferPoolManager::bg_flush_loop, this);
    }
    
    ~BufferPoolManager() {
        bg_flush_running_ = false;
        bg_flush_cv_.notify_all();
        if (bg_flush_thread_.joinable()) bg_flush_thread_.join();
    }
};
```

### 9.4.2 IxCompare 模板特化 + exact_match_mode

**文件**：`src/index/ix_index_handle.h` 新增 IxCompare 类（参考 RushDB 实现）

**文件**：`src/execution/executor_index_scan.h` 新增：
```cpp
class IndexScanExecutor : public AbstractExecutor {
    bool exact_match_mode_ = false;
    char *exact_key_ = nullptr;
    bool exact_key_found_ = false;
    bool exact_key_consumed_ = false;
    
    // 构造函数中：
    if (is_exact_match_query(conds, index_meta_.cols_)) {
        setup_exact_match_mode(conds, index_meta_.cols_);
        return;
    }
    
    static bool is_exact_match_query(...) {
        // 检查所有索引列是否都有等值条件
    }
    
    // Next() 中：
    if (exact_match_mode_) {
        auto it = ih_->find_entry(exact_key_);
        if (it != ih_->end()) return fh_->get_record(*it);
        return nullptr;
    }
};
```

### 9.4.3 UPDATE 原地更新优化

**文件**：`src/execution/executor_update.h` 构造函数中添加：

```cpp
bool any_set_col_in_index_ = false;
for (const auto &set_clause : set_clauses_) {
    for (const auto &index : tab_.indexes) {
        for (const auto &index_col : index.cols) {
            if (index_col.name == set_clause.lhs.col_name) {
                any_set_col_in_index_ = true;
                break;
            }
        }
        if (any_set_col_in_index_) break;
    }
    if (any_set_col_in_index_) break;
}

// 在 Next() 开头
if (!any_set_col_in_index_) {
    // 原地更新：跳过所有 old_keys/new_keys 计算和索引 delete+insert
    for (auto &target : targets_) {
        // MVCC 版本链处理
        // WAL 日志
        // fh_->update_record（只改 heap，不动索引）
    }
    return nullptr;
}
```

### 9.4.4 ScalerAggPlanExecutor 标量聚合专用路径

**新增文件**：`src/execution/execution_scaler_group.h`

```cpp
class ScalerAggPlanExecutor : public AbstractExecutor {
    TabCol sel_col_;
    std::unique_ptr<AbstractExecutor> child_executor_;
    Value result_;
    bool computed_ = false;
    
    void performAggregation() {
        child_executor_->beginTuple();
        int count = 0;
        float sum = 0.0f;
        bool first = true;
        
        for (; !child_executor_->is_end(); child_executor_->nextTuple()) {
            auto record = child_executor_->Next();
            // 根据 aggFuncType 累加
        }
        // 设置 result_
    }
};
```

### 9.4.5 后台 WAL flush 线程

**文件**：`src/recovery/log_manager.h` 新增

```cpp
class LogManager {
    std::atomic<lsn_t> durable_lsn_{INVALID_LSN};
    std::thread bg_flush_thread_;
    std::condition_variable commit_cv_;
    std::mutex commit_mutex_;
    
    void bg_flush_loop() {
        while (running_) {
            // 等待条件：buffer 满 80% / 距上次 flush 超 500us / 等待事务数超阈值
            flush_log_to_disk_unlocked();
            durable_lsn_.store(persist_lsn_);
            commit_cv_.notify_all();
        }
    }
    
public:
    void wait_for_durable(lsn_t my_lsn) {
        std::unique_lock<std::mutex> lk(commit_mutex_);
        commit_cv_.wait(lk, [&] { return durable_lsn_.load() >= my_lsn; });
    }
};
```

**commit 路径改造**：
```cpp
// 旧：log_manager->flush_up_to(lsn);
// 新：log_manager->wait_for_durable(lsn);
```

## 9.5 P2 实施指南（第 22-35 天）

### 9.5.1 PageGuard + RWLatch

**新增文件**：`src/storage/rwlatch.h`

```cpp
#pragma once
#include <shared_mutex>
class RWLatch {
public:
    void WLock() { mutex_.lock(); }
    void WUnlock() { mutex_.unlock(); }
    void RLock() { mutex_.lock_shared(); }
    void RUnlock() { mutex_.unlock_shared(); }
private:
    std::shared_mutex mutex_;
};
```

**新增文件**：`src/storage/page_guard.h`（参考 Kosthi 实现）

**修改**：`src/storage/page.h` 给 Page 类加 `RWLatch latch_`

**修改**：`src/index/ix_index_handle.h` 实现 Crab Protocol（节点级 latch）

### 9.5.2 NUMA 感知

```cpp
// 在 client_handler 开头
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(thread_id % 20, &cpuset);  // 绑定到 node0 的 0-19 核
pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

// 缓冲池内存分配
void *mem = numa_alloc_onnode(pool_size * PAGE_SIZE, 0);  // node0
```

### 9.5.3 AVX-512 加速

```cpp
// ix_compare 用 AVX-512
inline int ix_compare_avx512(const char *a, const char *b, int col_len) {
    __m512i va = _mm512_loadu_si512(a);
    __m512i vb = _mm512_loadu_si512(b);
    __mmask16 mask = _mm512_cmpneq_epi8_mask(va, vb);
    if (mask == 0) return 0;
    // 找第一个不同的字节
}
```

### 9.5.4 透明大页

```cpp
// 缓冲池内存分配后
madvise(pages_, pool_size_ * sizeof(Page), MADV_HUGEPAGE);
```

---

# 第十部分：备赛路线图与时间线

## 10.1 修订后的优先级表

| 优先级 | 优化项 | 预期收益 | 实施难度 | 风险 | 源码验证 |
|--------|-------|---------|---------|------|---------|
| 🔥🔥 P0-0 | **放开显式事务串行化** | **+400%~900%** | 低（1 行） | 高 | ✅ 已确认串行化 |
| 🔥🔥 P0-1 | **编译优化** `-O3 -DNDEBUG` | **+30%~50%** | 低（CMake 1 行） | 低 | ✅ 已确认无优化 |
| 🔥🔥 P0-2 | **UPDATE 列自引用支持** | 一致性可过 | 中（4 层） | 中 | ✅ 已确认不支持 |
| 🔥 P0-3 | 修复测试数据 | 本地可测 | 低 | 低 | ✅ 已确认未修复 |
| 🔥 P0-4 | 提升 MAX_CONN_LIMIT 8→256 | 避免连接拒绝 | 低 | 低 | ✅ 已确认不足 |
| 🔥 P0-5 | 缩小 buffer_mutex 范围 | +3%~8% | 低 | 低 | ✅ 已确认串行 |
| P1-1 | reentrant parser 改造 | +5%~15% | 高 | 中 | ✅ 已确认需改造 |
| P1-2 | 后台刷脏页线程 | +8%~25% | 中 | 中 | ✅ 已确认无后台刷 |
| P1-3 | IxCompare 模板特化 + exact_match | +10%~20% | 中 | 低 | ✅ 已确认无特化 |
| P1-4 | UPDATE 原地更新优化 | +10%~15% | 中 | 低 | ✅ 已确认无优化 |
| P1-5 | 后台 WAL flush 线程 | +10%~30% | 高 | 高 | ✅ 已确认仍同步 write |
| P1-6 | ScalerAggPlanExecutor | +5%~10% | 中 | 低 | ✅ 已确认无专用路径 |
| P2-1 | PageGuard + RWLatch + 页级 latch | +20%~40% | 极高 | 高 | ✅ 已确认无 PageGuard |
| P2-2 | B+树 Crab Protocol | +15%~30% | 高 | 高 | ✅ 已确认只有 root_latch_ |
| P2-3 | NUMA 感知 | +10%~20% | 中 | 中 | - |
| P2-4 | AVX-512 加速 | +5%~15% | 中 | 低 | - |
| P2-5 | 透明大页 | +5%~10% | 低 | 低 | - |

## 10.2 推荐时间线

### 第 1 天（立即）：3 项 1 行改动

1. `src/rmdb.cpp:41` `MAX_CONN_LIMIT 8` → `256`
2. `src/rmdb.cpp:50` `kExplicitTxnAdmissionLimit = 1` → `16`
3. `src/test/performance_test/table_data/warehouse.csv` `w_ytd` 3000.5 → 90001.5
4. CMakeLists.txt 加 `-O3 -DNDEBUG -march=native -flto`

**验证**：跑完整 `pre_submit_check.sh`，确认正确性。

### 第 2-3 天：编译优化 + UPDATE 列自引用

5. 编译优化（如果第 1 天未完成）
6. 修复 UPDATE 列自引用（4 层修改）

**验证**：跑 TPC-C benchmark，对比 tpmC。

### 第 4-7 天：P0 收尾 + P1 启动

7. 缩小 buffer_mutex 范围（do_analyze 移出锁外）
8. 启动 reentrant parser 改造（如果时间允许）
9. 启动后台刷脏页线程

### 第 8-21 天：P1 全部完成

10. IxCompare 模板特化 + exact_match_mode
11. UPDATE 原地更新优化
12. 后台 WAL flush 线程
13. ScalerAggPlanExecutor

### 第 22-35 天：P2 最终冲高

14. PageGuard + RWLatch
15. B+树 Crab Protocol
16. NUMA 感知
17. AVX-512 加速
18. 透明大页

### 决赛前 5 天（稳定性期）

- 停止新优化，只做 bug fix
- 每天跑 `oj_submit_check.sh` 3 轮
- 确认功能测试、load data、crash recovery、一致性检查全部 PASS
- 确认 tpmC 稳定（3 轮中位数波动 < 10%）

## 10.3 修订后的 tpmC 预测

| 阶段 | 预计 tpmC | 关键改动 |
|------|----------|---------|
| 当前基线 | 409 | （串行化准入 + 无编译优化） |
| P0-0 完成（放开串行化） | **1500~3000** | 1 行改动，但需验证正确性 |
| P0-1 完成（编译优化） | **2000~4000** | +30%~50% |
| P0-2 完成（UPDATE 列自引用） | **2000~4000** | 一致性可过（不直接提升 tpmC，但避免 0 分） |
| P1 全部完成 | **3000~6000** | +50%~100% |
| P2 全部完成 | **5000~10000+** | +50%~100% |

---

# 第十一部分：风险管理与应对

## 11.1 风险一：放开串行化暴露并发 bug

**风险**：`kExplicitTxnAdmissionLimit = 16` 后，MVCC + SSI 在真并发下可能暴露数据竞争。

**应对**：
- 先备份当前分支
- 先试 `kExplicitTxnAdmissionLimit = 4`，再 8，再 16
- 每一步跑完整 `pre_submit_check.sh`
- 用 `show execution_stats` 查看 abort 原因分布
- 如果 abort 率 > 50%，针对性修复 SSI/MVCC 并发 bug

## 11.2 风险二：编译优化改变未定义行为

**风险**：`-O3` 可能暴露 data race（特别是 MVCC 版本链的并发访问）。

**应对**：
- 先用 `-O2` 过渡，确认稳定后再 `-O3`
- 如果开启 `-O3` 后出现 segfault 或数据损坏，用 ThreadSanitizer 检测：
  ```bash
  g++ -fsanitize=thread ... 
  ```
- 必要时回退到 `-O2`

## 11.3 风险三：UPDATE 列自引用修改面广

**风险**：涉及 parser/ast/analyze/executor 四层，可能影响 task-02 ~ task-07。

**应对**：
- 修改前先跑 `pre_submit_check.sh --quick` 确认基线
- 修改后跑完整 `pre_submit_check.sh`
- 用 git 分支隔离，无效就回退
- 特别关注 task-08（事务）和 task-09（隔离）的回归

## 11.4 风险四：后台刷脏页与 WAL 顺序

**风险**：后台线程刷脏页前，必须确认 `page_lsn <= persist_lsn`，否则破坏 WAL。

**应对**：
- 后台线程刷脏页前查询 `log_manager_->get_persist_lsn()`
- 只刷 `page_lsn <= persist_lsn` 的页
- 反复跑 `crash_recovery_*` 测试

## 11.5 风险五：硬编码优化误判

**风险**：某些通用优化可能被误判为硬编码。

**应对**：
- 严格遵守"不针对特定表名/字段名/SQL 文本"原则
- `IxCompare` 特化是按"列数和类型"特化，不按表名 → 安全
- `exact_match_mode_` 是按"查询条件特征"分流 → 安全
- 如有疑问，参考明泰公告原文："不得改变 SQL 原有语义，也不得产生 SQL 未声明的额外副作用"

## 11.6 风险六：评测波动

**风险**：初赛共享物理机，20%+ 波动正常。

**应对**：
- 本地 benchmark 用 `--measure 60 -r 3` 取中位数
- OJ 提测至少跑 3 轮
- 优化效果 < 10% 不 confidence，至少要 15%+ 才认定有效

## 11.7 风险七：PageGuard + Crab Protocol 实现风险

**风险**：PageGuard + RWMutex + Crab Protocol 改造涉及 storage/index/transaction 多层，bug 难调试。

**应对**：
- 放到最后阶段（P2-1），在其他优化都稳定后再做
- 用单元测试逐步验证（先 Page RWMutex，再 PageGuard，再 B+树 Crab）
- 每一步都跑完整正确性检查

---

# 第十二部分：总结与核心建议

## 12.1 团队当前定位

| 维度 | 评估 |
|------|------|
| **架构选型** | ⭐⭐⭐⭐⭐ MVCC + SSI + Group Commit + 16 分片 BufferPool，符合 2026 题面且工程化 |
| **文档体系** | ⭐⭐⭐⭐⭐ 五层文档 + NOT-DO 记录，远超一般参赛队 |
| **测试框架** | ⭐⭐⭐⭐⭐ 自建 testkit + OJ 提测检查，工程化程度高 |
| **当前性能** | ⭐⭐ 409 tpmC，但根本原因是串行化 + 无编译优化（非架构问题） |
| **优化空间** | ⭐⭐⭐⭐⭐ 大量 P0/P1 优化未做，且有两个"1 行改动"可带来 5~7x 提升 |

## 12.2 最关键的 3 条建议

### 建议 1：立即放开显式事务串行化 + 开编译优化

**这两项加起来只需改 2-3 行代码，预期带来 +400%~500% tpmC 提升**（从 409 到 2000~3000）。这是当前最大的低垂果实，是文档和 v3.0 报告都未识别的真正瓶颈。

### 建议 2：必须修复 UPDATE 列自引用

**不修复的后果是性能测试 0 分**。官方决赛 SQL 明确使用 `w_ytd = w_ytd + :h_amount` 语法，团队 parser 完全不支持。这需要 4 层修改（parser/ast/analyze/executor），工作量中等但必须做。

### 建议 3：严格走通用优化路线

**2026 题面比 2024/2025 严格得多**，明泰公告明确"绕过通用解析/优化/执行流程"算违规。RushDB 的双轨制、内存 B+树、解析器旁路等核心方案**全部不可借鉴**。团队的优化必须对任意表任意 SQL 都生效。

## 12.3 tpmC 预测路径

| 优化阶段 | 预计 tpmC | 累计提升 |
|---------|----------|---------|
| 当前基线 | 409 | - |
| P0 完成（串行化 + 编译优化 + UPDATE 列自引用 + 数据修复） | **2000~4000** | +400%~900% |
| P1 全部完成（reentrant parser + 后台刷脏 + IxCompare + 原地更新 + 后台 WAL flush + 标量聚合） | **3000~6000** | +600%~1400% |
| P2 全部完成（页级 latch + NUMA + AVX-512 + 透明大页） | **5000~10000+** | +1100%~2300% |

## 12.4 与 Kosthi/RushDB 的最终对比

| 维度 | Kosthi 2024 | RushDB 2025 | 团队 2026（预测） |
|------|------------|------------|----------------|
| 路线 | 2PL 保守 | 内存化激进 | MVCC + SSI 通用优化 |
| 决赛 tpmC | 8 万 | 3.2 万~16 万 | 5000~10000+ |
| 赛规风险 | 低 | 高 | 低（严格走通用路线） |
| 工程化程度 | 中 | 高 | **极高** |
| 可复现性 | 中 | 低 | **高** |

**团队的优势在于工程化和可复现性**——即使最终 tpmC 不如 Kosthi/RushDB 的高，但路线稳健、风险可控、且不依赖赛规漏洞。这种"堂堂正正"的优化路线在 2026 严格赛规下反而是最稳妥的。

## 12.5 一句话总结

> **团队当前 tpmC=409 的根本原因不是文档说的"buffer_mutex + 同步 fsync + 执行锁过大"，而是"显式事务被强制串行化（`kExplicitTxnAdmissionLimit=1`）+ 无编译优化（默认 -O0）+ UPDATE 不支持列自引用"。仅放开串行化 + 开 -O3 + 修复 UPDATE 列自引用这 3 项改动，预期可让 tpmC 从 409 跃升到 2000~3000（5~7x）。团队应立即执行"第 1 天 3 项 1 行改动"，验证后按 P0→P1→P2 路线推进，严格走通用优化路线，冲击决赛 5000~10000+ tpmC。**

---

# 附录

## 附录 A：团队文档体系索引

| 路径 | 用途 | 价值 |
|------|------|------|
| `CLAUDE.md` | 项目总入口 | 团队规范 |
| `docs/README.md` | 文档总入口 | 导航 |
| `docs/official-doc/` | 官方资料（使用文档、性能方案、项目结构、测试说明、SQL 示例、一致性规则） | 赛规依据 |
| `docs/dev-doc/` | 开发文档（架构总览、SQL pipeline、optimizer、storage、execution、task 分工） | 实现参考 |
| `docs/perf-doc/` | 11 模块性能参考文档 + NOT-DO.md | 优化起点 |
| `docs/problem-doc/` | task-01 ~ task-11 题面 | 题目边界 |
| `docs/debug-doc/` | 4 篇深度调试记录 | 避坑指南 |
| `docs/虚拟机报告.md` | 评测环境硬件分析 | 硬件利用 |
| `docs/比赛交流群信息汇总-07-03.md` | 官方答疑 | 必读 |

## 附录 B：关键赛规要点

| 要点 | 内容 |
|------|------|
| GitLab 仓库根目录 | 必须为 `rmdb` |
| 仓库大小限制 | ≤ 100M |
| 性能测试流程 | 30s 预热 + 360s 测量 × 3 轮，取中位数 |
| 正确性检查 | 功能测试 + load data + 一致性检查 + 崩溃恢复 |
| 并发与隔离 | 16 线程，隔离级别 ≥ RC |
| 排名依据 | **仅以 tpmC 为唯一排名依据** |
| 硬编码优化 | **违规，取消参赛资格** |
| 事务占比 | NewOrder 10/23, Payment 10/23, OrderStatus/Delivery/StockLevel 各 1/23 |
| 评测波动 | 初赛共享物理机 20%+ 正常 |

## 附录 C：优化方案速查表

| 优先级 | 优化项 | 预期收益 | 实施难度 | 风险 | 团队现状 |
|--------|-------|---------|---------|------|---------|
| 🔥🔥 P0-0 | 放开显式事务串行化 | +400%~900% | 低 | 高 | ❌ 待做 |
| 🔥🔥 P0-1 | 编译优化 -O3 -DNDEBUG | +30%~50% | 低 | 低 | ❌ 待做 |
| 🔥🔥 P0-2 | UPDATE 列自引用支持 | 一致性可过 | 中 | 中 | ❌ 待做 |
| 🔥 P0-3 | 修复测试数据 | 本地可测 | 低 | 低 | ❌ 待做 |
| 🔥 P0-4 | MAX_CONN_LIMIT 8→256 | 避免连接拒绝 | 低 | 低 | ❌ 待做 |
| 🔥 P0-5 | 缩小 buffer_mutex 范围 | +3%~8% | 低 | 低 | ❌ 待做 |
| P1-1 | reentrant parser 改造 | +5%~15% | 高 | 中 | ❌ 待做 |
| P1-2 | 后台刷脏页线程 | +8%~25% | 中 | 中 | ❌ 待做 |
| P1-3 | IxCompare 特化 + exact_match | +10%~20% | 中 | 低 | ❌ 待做 |
| P1-4 | UPDATE 原地更新优化 | +10%~15% | 中 | 低 | ❌ 待做 |
| P1-5 | 后台 WAL flush 线程 | +10%~30% | 高 | 高 | ❌ 待做 |
| P1-6 | ScalerAggPlanExecutor | +5%~10% | 中 | 低 | ❌ 待做 |
| P2-1 | 页级 latch | +20%~40% | 极高 | 高 | ❌ 待做 |
| P2-2 | NUMA 感知 | +10%~20% | 中 | 中 | ❌ 待做 |
| P2-3 | AVX-512 加速 | +5%~15% | 中 | 低 | ❌ 待做 |
| P2-4 | 透明大页 | +5%~10% | 低 | 低 | ❌ 待做 |

## 附录 D：参考资源

| 资源 | 链接 | 用途 |
|------|------|------|
| Kosthi 2024 源码 | https://github.com/Kosthi/CSCC-DB-Rucbase-2024 | 保守路线参考 |
| RushDB 2025 源码 | https://github.com/RushDB-Lab/CSCC-DB-Rucbase-2025 | 微优化参考 |
| 官方 rucbase-lab | https://github.com/ruc-deke/rucbase-lab | 原版框架 |
| Kosthi TPCC-Tester | https://github.com/Kosthi/TPCC-Tester | TPC-C 测试脚本 |
| Kosthi Issue#1 | https://github.com/Kosthi/CSCC-DB-Rucbase-2024/issues/1 | 优化思路讨论 |
| parallel_hashmap | https://github.com/greg7mdp/parallel-hashmap | 仅参考 IxCompare 思路 |
| CMU 15-445 BusTub | https://github.com/cmu-db/bustub | PageGuard / Crab Protocol 参考 |
| 比赛官网 | https://db.educg.net | 赛规与公告 |
| 官方交流群 | QQ 群 529358791 | 答疑 |

## 附录 E：本报告整合的历史版本

| 版本 | 内容 | 状态 |
|------|------|------|
| v1.0 | 开源项目深度分析（Kosthi + RushDB 源码） | 已整合 |
| v2.0 | Git 历史挖掘（290 条提交） | 已整合 |
| v3.0 | 团队文档解析（2026-rmdb-docs.zip） | 已整合 |
| v4.0 | 源码逐行验证（2026-our-源码.zip） | 已整合 |
| **v5.0** | **最终整合版（本报告）** | **当前** |

---

**报告完**

*本报告整合了整个对话过程中 5 轮研究的全部成果：开源项目深度分析 + 获奖项目 Git 历史挖掘 + 团队文档体系解析 + 团队源码逐行验证。报告严格遵循 2026 题面赛规（禁止硬编码优化、要求崩溃恢复、要求数据一致性），所有建议均针对团队当前真实进展（task-11 性能优化阶段，AC 409 tpmC）。最重要的发现是：当前 tpmC=409 的根本原因是"显式事务串行化 + 无编译优化 + UPDATE 不支持列自引用"，3 项改动预期带来 5~7x 提升。建议立即按"第 1 天 3 项 1 行改动"执行，验证后按 P0→P1→P2 路线推进，冲击决赛 5000~10000+ tpmC。*
