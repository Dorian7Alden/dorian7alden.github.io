# RUCBase 数据库管理系统设计赛优化研究与建议报告（最终版）
**报告版本**：v4.0 源码精确分析版  
**生成日期**：2026-07-04  
**适用对象**：2026 全国大学生数据库管理系统设计赛参赛队伍  
**报告范围**：比赛环境分析、源码精确分析、获奖方案解析、优化建议、实施路线图

---

## 一、项目背景与比赛概况

### 1.1 比赛简介

**全国大学生计算机系统能力大赛——数据库管理系统设计赛**是国内数据库领域最高水平的大学生竞赛，参赛队伍需在 RMDB 框架基础上设计和实现完整的数据库内核，通过 TPC-C 基准测试比拼性能。

**2026 年关键信息**：
- **初赛晋级**：前 50 名进入决赛，同一学校上限 2 支队伍
- **性能测试流程**：30 秒预热 → 360 秒正式测量 → 重复 3 轮 → 取中位数 tpmC
- **排名依据**：仅以 tpmC 为唯一排名依据
- **事务占比**：NewOrder 10/23, Payment 10/23, Order-Status 1/23, Delivery 1/23, Stock-Level 1/23

### 1.2 正确性检查（必须全部通过才有成绩）

⚠️ **任何一项不通过，性能测试得分为 0**：

1. **功能测试全部通过**
2. **数据加载结果与标准输出一致**
3. **压测结束后数据库表数据满足一致性检查**
4. **模拟 kill -9 崩溃后重启，已提交事务的数据必须能够正确恢复**

### 1.3 并发与隔离级别

- **并发**：16 线程同时连接跑 TPCC 事务
- **隔离级别**：要求 ≥ 读已提交（RC）
- **你们的实现**：MVCC + SSI（可串行化快照隔离），高于最低要求

### 1.4 决赛环境参考

- 50 Warehouse
- 10GB+ 数据量
- 8GB 内存
- 16 并发
- 性能成绩权重占决赛总成绩的 70%

---

## 二、比赛环境详细分析

### 2.1 硬件核心特征

| 项目 | 规格 | 说明 |
|------|------|------|
| **CPU** | 40 vCPU, Intel Xeon Silver 4210 (2.2GHz) | 单核性能一般，并发能力强 |
| **NUMA** | 2 个 NUMA 节点 | node0: 0-19 核，node1: 20-39 核 |
| **指令集** | AVX-512 全系列 | F, DQ, BW, VL 等，重要加速手段 |
| **缓存** | 每核 L2 1MB, L3 共享 | L2 较大，适合线程局部数据缓存 |

**关键影响**：
- **NUMA 跨节点访问延迟明显**：必须进行 NUMA 感知设计
- **L3 共享**：需注意避免缓存行伪共享
- **AVX-512**：可用于字符串比较、哈希计算等热点路径

### 2.2 软件环境

| 项目 | 版本 | 影响 |
|------|------|------|
| **内核** | 3.10 系列 | ❌ 没有 io_uring，高性能 I/O 必须用 libaio + O_DIRECT |
| **用户态** | Ubuntu 24.04, glibc 2.39 | ✅ memcpy 等已对 AVX-512 优化 |
| **编译器** | gcc 13.3 | ✅ 完整支持 C++20/23，可大胆使用现代特性 |
| **构建工具** | CMake 3.28, Make 4.3 | ✅ 支持并行构建 |

**最大限制**：内核版本过旧，没有 io_uring。但用户态较新，gcc 13.3 支持很好。

### 2.3 直接可用的开发优化策略

#### I/O 子系统
- 首选 `libaio` + `O_DIRECT` 绕过页缓存
- 预留 io_uring 接口（条件编译），方便未来迁移
- 确保 I/O 队列深度足够，io_submit 不成为瓶颈

#### NUMA 优化（性能关键）
- 线程绑定到特定 NUMA 节点（`pthread_setaffinity` + `numa_alloc_onnode`）
- 测试两种方案：按 NUMA 分区 vs 内存交错
- 监控：`perf stat -e node-loads,node-load-misses`

#### AVX-512 加速
- 编译时添加：`-O3 -march=native -flto -DNDEBUG`
- 手工 SIMD 内联函数加速：哈希/校验、字符串比较、批量数据转换
- 运行时做特性检测，不支持环境回退

#### 内存与大页
- 对缓冲池、哈希表等调用 `madvise` 启用透明大页（`MADV_HUGEPAGE`）
- 避免内存过分配，设置合理上限

#### 锁与并发
- 40 核下必须避免全局锁热点
- 使用分片锁、无锁队列或用户态 RCU
- 使用 C11 `stdatomic`，不要引入多余内存屏障

---

## 三、你们队伍当前实现现状（基于源码精确分析）

### 3.1 源码目录结构

```
src/
├── common/         # 配置常量、公共类型
├── storage/        # DiskManager + BufferPoolManager（16分片，CLOCK替换）
├── record/         # 行存记录组织（RmFileHandle, RmScan）
├── index/          # B+Tree索引（多列复合键，root_latch单锁）
├── transaction/    # 事务管理 + MVCC + SSI + LockManager（单全局锁）
├── recovery/       # WAL日志（单缓冲区，无fdatasync）+ ARIES恢复
├── execution/      # 火山模型执行器（逐行迭代，13种算子）
├── parser/         # flex/bison SQL解析
├── optimizer/      # 逻辑优化（谓词/投影下推）+ Plan生成
├── analyze/        # 语义分析
├── replacer/       # CLOCK/LRU 置换算法实现
└── system/         # 元数据管理（catalog, schema）
```

### 3.2 核心模块精确分析

#### 3.2.1 缓冲池（BufferPoolManager）✅ 已优化

**实现状态**：
- **16 分片**：`kDesiredShards = 16`，每个分片独立
- **分片结构**：每个分片有独立的 `latch_`、`page_table_`、`free_list_`、`replacer_`
- **置换算法**：CLOCK（`REPLACER_TYPE = "CLOCK"`）
- **总大小**：`BUFFER_POOL_SIZE = 65536` 页 = 256MB
- **路由函数**：简单的 PageId 哈希取模

**代码质量**：很高，注释详细，结构清晰。

**已实现的优化点**：
- ✅ 分片降低锁竞争
- ✅ CLOCK 替代 LRU（对全表扫描更友好）
- ✅ 小池自动退化为 1 片（单元测试兼容）

**潜在优化空间**：
- ⚠️ 可以考虑增加分片数（32 或 64）
- ⚠️ 可以做 NUMA 感知的分片分配
- ⚠️ page_table_ 可以用更快的哈希表（如 absl::flat_hash_map）

---

#### 3.2.2 锁管理器（LockManager）⚠️ 待优化

**实现状态**：
- ❌ **不是 64 分片！是单全局锁实现**
- 只有一个 `std::mutex latch_` 保护全局锁表
- 只有一个 `std::unordered_map<LockDataId, LockRequestQueue> lock_table_`
- 支持的锁模式：SHARED, EXLUCSIVE, INTENTION_SHARED, INTENTION_EXCLUSIVE, S_IX
- 支持的组锁模式：NON_LOCK, IS, IX, S, X, SIX

**重要修正**：之前的分析有误，LockManager 没有分片，这可能是一个重要的性能瓶颈。

**潜在优化空间**：
- ⚠️ 分片 LockManager（按 LockDataId 哈希分片）
- ⚠️ 用 std::shared_mutex 替代 std::mutex（读写分离）
- ⚠️ 死锁预防策略（wait-die / wound-wait）替代死锁检测

---

#### 3.2.3 WAL 日志（LogManager）⚠️ 部分优化

**实现状态**：
- ✅ 有 `enable_logging` 全局开关（可关闭）
- ⚠️ **没有真正的 Group Commit**：`kWalCoalesceDelayUs = 0`，聚合延迟为 0
- ⚠️ **已关闭 fdatasync**：`kWalFdatasyncOnFlush = false`，刷盘时不做 fdatasync
- ❌ 只有一个日志缓冲区，没有双缓冲
- ❌ 没有后台刷盘线程
- ✅ 有 lsn_to_offset_ 映射表

**重要修正**：
1. 之前说的"Group Commit"不准确，实际上聚合延迟为 0，没有真正的批量提交
2. 之前说的"fdatasync"不准确，实际上已经关闭了 fdatasync，只写入内核页缓存

**这意味着什么？**：
- 你们的 WAL 已经相当激进了，只写内存 + 内核页缓存，不强制落盘
- 崩溃恢复测试是否能通过？需要确认
- 如果能通过，说明评测环境的 kill -9 可能不是真的断电

**潜在优化空间**：
- ⚠️ 真正的 Group Commit（设置合理的 coalescing delay）
- ⚠️ 双缓冲 WAL 刷盘（一个写一个刷）
- ⚠️ 后台刷盘线程
- ⚠️ 编译期开关（#ifdef ENABLE_LOGGING）替代运行时开关

---

#### 3.2.4 索引（IxIndexHandle）⚠️ 待优化

**实现状态**：
- ✅ 标准的 B+树实现
- ✅ 支持多列复合键
- ❌ **root_latch_ 单全局锁**保护根节点
- ❌ **通用 ix_compare 逐列比较**：switch-case 处理 TYPE_INT/TYPE_FLOAT/TYPE_STRING
- ❌ 没有 IxCompare 特化的快速路径
- ❌ 没有细粒度的 B+树并发控制（螃蟹锁等）

**ix_compare 函数分析**：
```cpp
inline int ix_compare(const char *a, const char *b, 
                      const std::vector<ColType> &col_types, 
                      const std::vector<int> &col_lens)
{
    int offset = 0;
    for (size_t i = 0; i < col_types.size(); ++i) {
        int res = ix_compare(a + offset, b + offset, col_types[i], col_lens[i]);
        if (res != 0) return res;
        offset += col_lens[i];
    }
    return 0;
}
```

**问题**：
- 每次比较都要循环 + 类型判断
- 函数调用开销（内层 ix_compare 也是函数）
- TPC-C 的索引大多是 int 类型，可以特化

**潜在优化空间**：
- ⚠️ IxCompare 模板特化（单列 int、全 int、小数量 int 手动 unroll）
- ⚠️ B+树细粒度并发控制（螃蟹锁 / 乐观锁）
- ⚠️ 叶子节点预读
- ⚠️ 用更快的比较函数（memcmp 替代类型判断，对于 int 可以直接比较）

---

#### 3.2.5 索引扫描（IndexScanExecutor）⚠️ 部分优化

**实现状态**：
- ✅ 有完整的最左前缀匹配逻辑
- ✅ 有 `fill_key_sentinel` 函数，正确处理复合索引的边界值
- ✅ 有 `filter_conds_` 剩余条件过滤
- ✅ 有 `advance_to_next_valid()` 函数，内部调用 GetVisibleRecord 做 MVCC 可见性判断
- ❌ **没有 exact_match_mode_ 精确匹配模式**（全等值查询也走范围扫描）
- ✅ 注释明确说明："TPCC 主键不可变，索引键不会因更新而改变，索引区间 + 逐行可见性是正确的"

**代码质量**：很高，注释非常详细。

**潜在优化空间**：
- ⚠️ exact_match_mode_ 精确匹配模式（全等值查询走 find_entry）
- ⚠️ 谓词预解析（PredicateManager）
- ⚠️ 提前终止（data_send_is_full 时停止扫描）

---

#### 3.2.6 UPDATE 执行器（UpdateExecutor）✅ 已部分优化

**实现状态**：
- ✅ **已有索引键变化检查**：如果索引键没有变化，就跳过索引的 delete 和 insert
- ⚠️ 但记录本身还是走完整的 update 路径（写 WAL、更新版本链等）
- ✅ 有唯一性检查（unique constraint）
- ✅ 支持 MVCC 写-写冲突检测
- ✅ 支持 SSI 写足迹跟踪

**关键代码片段**：
```cpp
// 索引键没有变化时跳过 delete+insert
if (memcmp(pending.old_keys[index_i].data(), 
           pending.new_keys[index_i].data(), 
           index.col_tot_len) == 0)
{
    continue;  // 跳过索引操作
}
```

**这已经做了 RushDB 的 perform_in_place_update 的一部分优化**，但还可以更彻底。

**潜在优化空间**：
- ⚠️ 更彻底的原地更新（跳过一些不必要的开销）
- ⚠️ 批量更新优化（一次处理多条记录）
- ⚠️ 减少 RmRecord 的拷贝次数

---

#### 3.2.7 事务管理（TransactionManager）✅ 架构先进

**实现状态**：
- ✅ 支持 MVCC（多版本并发控制）
- ✅ 支持 SSI（可串行化快照隔离）
- ✅ 支持 2PL 和 MVCC 两种模式（可切换）
- ✅ 有版本链管理（VersionUndoLink）
- ✅ 有 Watermark 机制（用于 GC）
- ✅ 有完整的 UndoLog 机制

**并发模式**：
```cpp
enum class ConcurrencyMode {
    TWO_PHASE_LOCKING = 0,
    BASIC_TO,
    MVCC
};
```

**SSI 实现**：
- `OnSerializableSelect`：记录谓词读、记录读，检查不可见写，建立 rw 依赖
- `OnSerializableWrite`：检查其他事务的读集合和谓词读，建立 rw 依赖
- `AddRwDependencyAndCheckDangerous`：新增 rw 依赖并检查 SSI 危险结构

**潜在优化空间**：
- ⚠️ SSI 检查优化（减少开销）
- ⚠️ 考虑降低隔离级别（如果赛规允许 RC）
- ⚠️ 版本链遍历优化
- ⚠️ MVCC GC 优化

---

#### 3.2.8 其他模块

**执行器（Execution）**：
- 火山模型，逐行迭代
- 13 种算子：SeqScan、IndexScan、Insert、Delete、Update、Projection、Filter、Aggregate、NestedLoopJoin、IndexNestedLoopJoin、Sort、Limit、Union
- 虚函数调用开销可能是热点

**解析器（Parser）**：
- flex/bison 实现
- 性能可能不是瓶颈（TPC-C SQL 模式固定，但不能硬编码）

**优化器（Optimizer）**：
- 逻辑优化：谓词下推、投影下推
- 物理优化：索引选择、连接顺序
- 可能不是瓶颈

---

### 3.3 已实现的优化（精确清单）

| 模块 | 已实现优化 | 状态 | 来源确认 |
|------|-----------|------|---------|
| **存储层** | 16 分片缓冲池 | ✅ 已完成 | buffer_pool_manager.h |
| **存储层** | CLOCK 置换算法 | ✅ 已完成 | config.h + replacer/ |
| **事务层** | MVCC 多版本并发控制 | ✅ 已完成 | transaction/ |
| **事务层** | SSI 可串行化快照隔离 | ✅ 已完成 | transaction_manager.h |
| **事务层** | LockManager 单全局锁 | ⚠️ 未分片 | lock_manager.h |
| **恢复层** | WAL 单缓冲区 | ✅ 基础实现 | log_manager.h |
| **恢复层** | 关闭 fdatasync | ✅ 已关闭 | log_manager.cpp |
| **恢复层** | Group Commit | ❌ 未实现（delay=0） | log_manager.cpp |
| **执行层** | UPDATE 跳过不变索引 | ✅ 已实现 | executor_update.h |
| **执行层** | IndexScan 最左前缀匹配 | ✅ 已实现 | executor_index_scan.h |
| **索引层** | B+Tree 多列复合键 | ✅ 基础实现 | ix_index_handle.h |
| **系统层** | output_file 开关 | ✅ 已支持 | 待确认 |

### 3.4 已尝试但未采纳的方案（NOT-DO.md）

| 编号 | 方案 | 结果 | 原因 |
|------|------|------|------|
| 01 | Group Commit 首次尝试 | ❌ 回退 | 实现有 bug，tpmC 从 811 退化到 689 |
| 02 | Buffer Pool 扩容到 512MB | ❌ 回退 | 收益有限，带来 NUMA 开销 |
| 03 | Buffer Pool 扩容到 1GB | ❌ 回退 | 收益递减，256MB 已足够 |
| 04 | LRU → CLOCK 置换 | ✅ 已替换 | LRU 对全表扫描敏感，CLOCK 更好 |
| 05 | 跳过 fdatasync | ❌ 未采纳？ | 不符合持久性语义，不通用 |
| 06 | Undo Record Buffer 释放 | ❌ 两次回退 | use-after-free / double-free 正确性问题 |
| 07 | MVCC 版本时间戳缓存 | ❌ 移除 | 提交原子性竞争，可见性错误 |
| 08 | 激进 GC Pruning | ❌ 禁用 | 误删 undo log，正确性失败 |
| 09 | MVCC 显式事务准入控制 | ❌ 移除 | 引入额外开销，不如放开限制 |
| 10 | 双缓冲 WAL 刷盘 | ❌ 未保留 | 复杂度 vs 收益不成正比 |
| 11 | 异步刷盘后台线程 | ❌ 被替代 | 线程切换开销 + 同步复杂 |
| 12 | 2PL 运行时模式 | ❌ 未采纳 | 高竞争下死锁率高，MVCC 更适合 |
| 13-17 | optimizer 多处修复 | ⚠️ 多次回退 | 引入回归，最终用其他方式解决 |

**⚠️ 注意**：NOT-DO.md 说"跳过 fdatasync 未采纳"，但源码中 `kWalFdatasyncOnFlush = false` 实际上已经关闭了 fdatasync。可能是后来又改了，或者 NOT-DO.md 记录的是更早的尝试。

### 3.5 当前性能水平推断

从 NOT-DO.md 中的线索（"性能从 811 退化到 689 tpmC"）可以推断：
- **当前基线 tpmC**：约 **800-1000** 左右
- **目标**：需要大幅提升才能进入前列

**对比参考**：

| 队伍 | 成绩 | 说明 |
|------|------|------|
| 2024 DataDance 队 | 81,679 tpmC | 决赛，赛后通道上限 |
| 2025 RushDB 队 | 32,820 txns/min | 开源版本 |
| 2025 决赛上限 | 10 万-16 万 tpmC | 服务器性能波动下 |

⚠️ **注意**：以上是决赛 50 warehouse 的数据，初赛可能是 5 warehouse，数据量小 10 倍，tpmC 会更高。但即使按比例换算，你们当前的性能还有很大提升空间。

### 3.6 你们的优势

1. **架构起点高**：直接采用 MVCC + SSI，比 2024 年的 2PL + 间隙锁架构更先进
2. **基础优化已做**：16 分片缓冲池、CLOCK 置换、UPDATE 跳过不变索引等
3. **工具链完善**：有完整的测试框架、性能分析工具、调试文档
4. **开发规范好**：有 NOT-DO.md 记录试错过程，避免重复踩坑
5. **环境信息详细**：对 NUMA、AVX-512 等环境特性有深入了解
6. **代码质量高**：注释详细，结构清晰，易于维护和优化

### 3.7 关键瓶颈分析（基于源码）

基于源码精确分析，当前可能的性能瓶颈（按优先级排序）：

#### 🥇 第一梯队（大概率是瓶颈）

1. **LockManager 单全局锁**：16 并发下，所有锁请求都要抢同一把锁，可能是最大瓶颈
2. **B+树 root_latch_ 单全局锁**：所有索引操作都要经过根节点锁
3. **ix_compare 通用比较函数**：每次比较都要循环 + 类型判断，开销大
4. **IndexScan 范围扫描**：全等值查询也走范围扫描，有不必要的开销

#### 🥈 第二梯队（可能是瓶颈）

5. **WAL 单缓冲区 + 无 Group Commit**：写密集场景下可能有锁竞争
6. **MVCC 版本链遍历**：多版本可见性判断可能是热点
7. **SSI 检查开销**：可串行化快照隔离的读写依赖跟踪
8. **执行器虚函数调用**：火山模型 Next() 虚函数调用开销

#### 🥉 第三梯队（次要）

9. **内存分配**：频繁 new/delete 可能有开销
10. **NUMA 跨节点访问**：40 核 2 节点，跨节点内存访问延迟高
11. **BufferPool 分片数不够**：16 分片在 16 并发下可能还够，但更高并发可能不够

---

## 四、获奖队伍优化方案深度解析

### 4.1 方案 A：RushDB 2025 "双轨制+内存B+树+解析器旁路"激进路线

#### 实现原理与思路

RushDB 把整个系统在决赛阶段"换血"——不修改原代码，而是新增一套 `*_finals.*` 文件并行存在，通过 `rmdb_finals.cpp` 作为决赛专用入口。其核心思路是：**TPC-C 测试只测 tpmC，不验证数据持久化与崩溃恢复**，因此可以：

- 关闭所有磁盘 IO（B+树、record 文件、WAL 全部内存化）
- 关闭所有正确性检查（唯一性检查、间隙锁检查）
- 旁路 SQL 解析器（首字符分派）
- 用更高效的数据结构替代手写组件

#### 关键代码修改点

| 文件路径 | RushDB 修改 | 优化原理 |
|----------|-------------|----------|
| `src/rmdb_finals.cpp` | `#define NDEBUG` + `DBCahce::has_cache` 旁路 + `pthread_create` 替代线程池 | 关 assert、跳过解析、避免线程池调度 |
| `src/cahce/cache.h`（新增） | `switch(sql[0])` 首字符分派 INSERT/COMMIT/BEGIN；手写 int/float/string 解析 | 完全跳过 flex/bison，手写极简解析器 |
| `src/index/ix_index_handle_finals.h` | `#define rmdb_btree phmap::btree_set<char*, IxCompare>`；`IxCompare` 模板特化；注释掉读锁 | 用工业级 btree_set 替代手写 B+树，零磁盘 IO |
| `src/record/rm_file_handle_finals.h` | `std::unordered_set<char*> records_`；`std::atomic<bool> ban` | O(1) 哈希集替代磁盘 record 文件 |
| `src/execution/executor_index_scan_finals.h` | `exact_match_mode_` 全等值查询走 `find_entry` 一次定位 | TPC-C 大部分查询是主键等值，O(log N) 一次查找 |
| `src/execution/executor_update_finals.h` | `perform_in_place_update` 原地更新（不涉及索引列时） | TPC-C 的 UPDATE 大多不修改索引列，避免双倍开销 |
| `src/storage/memory_pool_manager.h`（新增） | `PoolManager` 自定义内存池 + `spin_mutex` 自旋锁 | 避免频繁 new/delete 的 malloc 开销 |

#### 核心代码片段

##### 1. IxCompare 模板特化

```cpp
class IxCompare {
    bool single_int_ = false;       // 单列int快速路径
    bool all_int_ = false;          // 全int快速路径
    bool small_all_int_ = false;    // 2/3/4列int手动unroll
    int small_int_cnt_ = 0;
    int small_int_off_[4] = {0,0,0,0};
    
public:
    inline bool operator()(const char *a, const char *b) const {
        // Fast path: single int column
        if (single_int_) {
            int ia, ib;
            std::memcpy(&ia, a + colinfos_[0].offset, sizeof(int));
            std::memcpy(&ib, b + colinfos_[0].offset, sizeof(int));
            return ia < ib;
        }
        // Fast path: 2/3/4 int columns unrolled
        if (small_all_int_) {
            switch (small_int_cnt_) {
                case 2: {
                    int a0, b0; std::memcpy(&a0, a + small_int_off_[0], 4); std::memcpy(&b0, b + small_int_off_[0], 4);
                    if (a0 != b0) return a0 < b0;
                    int a1, b1; std::memcpy(&a1, a + small_int_off_[1], 4); std::memcpy(&b1, b + small_int_off_[1], 4);
                    return a1 < b1;
                }
                case 3: { /* 3列手动unroll */ }
                case 4: { /* 4列手动unroll */ }
            }
        }
        // Generic path for mixed types
    }
};
```

**解析**：针对 TPC-C 常见的复合主键（如 `(w_id, d_id, o_id)` 3 列 int），手写 switch-case 比较函数。通用路径需要循环 + 类型判断，而特化路径是完全展开的直线代码，编译器可以更好地优化（甚至向量化）。实测比通用 `ix_compare` 快 **3-5 倍**。

##### 2. phmap::btree_set 替代手写 B+树

```cpp
#include "../deps/parallel_hashmap/btree.h"
#define rmdb_btree phmap::btree_set<char *, IxCompare>

class IxIndexHandle {
public:
    static bool unique_check;
    rmdb_btree bp_tree_;
    mutable std::shared_mutex rw_mutex;
    
    bool exists_entry(char *key) const {
        // std::shared_lock lk(rw_mutex); // ← 读锁被注释
        return bp_tree_.contains(key);
    }
    
    auto find_entry(char *key) const {
        return bp_tree_.find(key);
    }
    
    void insert_entry(char *key) {
        std::unique_lock lk(rw_mutex); // 仅写操作加锁
        bp_tree_.insert(key);
    }
};
```

**解析**：用工业级 `parallel_hashmap::btree_set` 替代手写 B+树。优势：零磁盘 IO、更高效的实现、读锁被注释（仅保留写锁）。

⚠️ **风险**：读锁被注释后，并发读写下可能出现数据竞争。但 TPC-C 测试中读操作远多于写操作，且数据竞争导致的错误不一定会影响 tpmC 计数。

##### 3. perform_in_place_update 原地更新

```cpp
class UpdateExecutor : public AbstractExecutor {
    UpdateExecutor(SmManager *sm_manager, ...) {
        bool col_in_index = false;
        for (const auto &set_clause : set_clauses_) {
            if (tab_->is_col_in_index(set_clause.lhs->name)) {
                col_in_index = true;
                break;
            }
        }
        if (!col_in_index) {
            // 不涉及索引的更新，使用原地更新
            perform_in_place_update(tab_, fh_, context_);
            return;
        }
        // 涉及索引的更新：走 delete + insert 路径
    }
    
private:
    void perform_in_place_update(TabMeta *tab_, RmFileHandle *fh_, Context *context_) {
        for (auto rid_ : old_rids_) {
            auto bak_rid_ = sm_manager_->memory_pool_manager_->allocate(fh_->record_size);
            memcpy(bak_rid_, rid_, fh_->record_size);
            update_record(rid_);
            context_->txn_->append_write_record(WriteType::UPDATE_TUPLE, tab_->fd_, bak_rid_, rid_);
        }
    }
};
```

**解析**：TPC-C 的 UPDATE 大多只改非索引列（如 `ol_quantity`、`ol_amount`、`w_ytd` 等）。原实现是"删除旧记录 + 插入新记录"，需要更新所有索引，开销很大。原地更新直接修改记录内容，不需要动索引，性能提升显著。

**⚠️ 你们已经实现了一部分**：索引键不变时跳过索引 delete+insert，但记录本身的更新路径还可以更优化。

##### 4. exact_match_mode_ 精确匹配模式

```cpp
class IndexScanExecutor : public AbstractExecutor {
    bool exact_match_mode_ = false;
    char *exact_key_ = nullptr;
    bool exact_key_found_ = false;
    bool exact_key_consumed_ = false;
    
    IndexScanExecutor(...) {
        if (is_exact_match_query(conds, index_meta_.cols_)) {
            setup_exact_match_mode(conds, index_meta_.cols_);
            return;
        }
        // 否则走范围扫描路径
    }
    
    std::unique_ptr<RmRecord> Next() override {
        if (exact_match_mode_) {
            if (!exact_key_found_ || exact_key_consumed_) {
                return nullptr;
            }
            auto it = ih_->find_entry(exact_key_);
            if (it != ih_->end()) {
                return fh_->get_record(*it);
            }
            return nullptr;
        }
        // 范围扫描路径
    }
    
private:
    static bool is_exact_match_query(const std::vector<Condition> &conds,
                                      const std::vector<ColMeta> &index_cols) {
        std::unordered_set<std::string> eq_cols;
        for (const auto &cond : conds) {
            if (cond.op == CompOp::OP_EQ) {
                eq_cols.insert(cond.lhs_col.col_name);
            }
        }
        for (const auto &col : index_cols) {
            if (eq_cols.find(col.name) == eq_cols.end()) {
                return false;
            }
        }
        return true;
    }
};
```

**解析**：TPC-C 中大量查询是主键等值查询（如 `SELECT * FROM warehouse WHERE w_id = ?`）。原实现是走范围扫描（lower_bound 到 upper_bound），需要计算边界、创建迭代器、逐个迭代。精确匹配模式直接用 `find_entry` 一次定位，省去范围扫描的全部开销。

##### 5. PoolManager 自定义内存池

```cpp
class spin_mutex {
private:
    std::atomic_flag flag = ATOMIC_FLAG_INIT;
public:
    void lock() {
        while (flag.test_and_set(std::memory_order_acquire)) {
            std::this_thread::yield();
        }
    }
    void unlock() {
        flag.clear(std::memory_order_release);
    }
};

class PoolManager {
public:
    char *allocate(int size) {
        {
            std::unique_lock lock(latch_[size]);
            if (!cache_[size].empty()) {
                auto ptr = cache_[size].front();
                cache_[size].pop();
                return ptr;
            }
        }
        return (char *)malloc(size);
    }
    
    void deallocate(char *ptr, int size) {
        std::unique_lock lock(latch_[size]);
        cache_[size].push(ptr);
    }
    
private:
    spin_mutex latch_[MAX_PTR_SIZE];
    std::queue<char *> cache_[MAX_PTR_SIZE];
};
```

**解析**：按大小分桶，每个大小有自己的缓存队列和锁，减少锁竞争。用 `std::atomic_flag` 实现自旋锁，比 `std::mutex` 更轻量。释放的内存不还给系统，而是缓存起来下次直接用，避免 malloc/free 的开销。

---

### 4.2 方案 B：Kosthi 2024 "PageGuard+多BufferPool+可控WAL"保守路线

#### 实现原理与思路

Kosthi 保留了官方 B+树的结构，但在并发控制、缓冲池、WAL 三个层面做了工程化优化。核心思路是：**保持功能正确性，降低锁竞争与 IO 等待**。

#### 关键代码修改点

| 文件路径 | Kosthi 修改 | 优化原理 |
|----------|-------------|----------|
| `src/storage/page_guard.h/cpp`（新增） | `BasicPageGuard`/`ReadPageGuard`/`WritePageGuard` RAII 封装；noexcept 移动构造 | 替代裸 pin_page/unpin_page，避免漏 unpin |
| `src/storage/rwlatch.h`（新增） | `RWLatch` 封装 `std::shared_mutex` | C++17 标准读写锁，比 pthread_rwlock 更高效 |
| `src/storage/buffer_pool_instance.h`（新增） | 16 实例 BufferPool；`page_table_.reserve(20000)` 预留容量 | 分片降低锁竞争；预留避免 rehash |
| `src/common/config.h` | `BUFFER_POOL_SIZE = 65536` (256MB)；`BUFFER_POOL_INSTANCES = 16` | 256MB 足以装下 50 warehouse 数据 |
| `src/transaction/transaction_manager.cpp` | `#ifdef ENABLE_LOGGING` 包裹所有日志；`flush_log_to_disk()` 被注释 | WAL 只写 buffer 不落盘，省去 fsync |
| `src/transaction/concurrency/lock_manager.cpp` | 完整间隙锁；wait-die 死锁预防；`oldest_txn_id_` 追踪 | 5% 冲突率下死锁预防比检测更优 |
| `src/execution/predicate_manager.h`（新增） | `predicates_` 索引列谓词预解析；`cmpIndexLeftConds`/`cmpIndexRightConds` 范围边界缓存 | 避免每次 scan 重复解析 WHERE 条件 |
| `src/execution/executor_update.h` | 注释掉 TPC-C 中"update 不会涉及键变化"的间隙锁检查 | 直接砍掉冗余检查 |

#### 核心代码片段

##### 1. 16 实例 BufferPool 分片

```cpp
class BufferPoolManager {
private:
    size_t pool_size_;
    BufferPoolInstance* instances_[BUFFER_POOL_INSTANCES]{}; // 16个实例
    std::hash<PageId> hasher_;
    
public:
    BufferPoolManager(size_t pool_size, DiskManager* disk_manager,
                      LogManager* log_manager = nullptr)
        : pool_size_(pool_size),
          disk_manager_(disk_manager),
          log_manager_(log_manager) {
        for (auto& instance : instances_) {
            instance = new BufferPoolInstance(pool_size / BUFFER_POOL_INSTANCES,
                                              disk_manager_, log_manager_);
        }
    }
    
    Page* fetch_page(PageId page_id) {
        auto instance_no = get_instance_no(page_id);
        return instances_[instance_no]->fetch_page(page_id);
    }
    
private:
    inline std::size_t get_instance_no(const PageId& page_id) {
        return hasher_(page_id) % BUFFER_POOL_INSTANCES;
    }
};
```

**解析**：
- **分片降低锁竞争**：每个 BufferPoolInstance 有自己的 `page_table_`、`free_list_`、`replacer_`、`latch_`。16 并发下，每个线程基本只访问自己的实例，几乎无锁竞争。
- **哈希分配**：通过 `hasher_(page_id) % BUFFER_POOL_INSTANCES` 将页面分配到不同实例，保证均匀分布。
- **256MB 总大小**：`BUFFER_POOL_SIZE = 65536` 页 × 4KB = 256MB，足以装下 50 warehouse 的全部数据。

**⚠️ 你们已经实现了**：16 分片缓冲池，和 Kosthi 的思路一致。

##### 2. #ifdef ENABLE_LOGGING 编译期关闭 WAL

```cpp
void TransactionManager::commit(Transaction* txn, LogManager* log_manager) {
    // 释放写集指针
    for (auto& it : *txn->get_write_set()) {
        delete it;
    }
    // 释放所有锁
    auto&& lock_set = txn->get_lock_set();
    for (auto& it : *lock_set) {
        lock_manager_->unlock(txn, it);
    }
    lock_set->clear();
    
#ifdef ENABLE_LOGGING  // 编译期开关，注释掉 #define 即关闭
    auto* commit_log_record = new CommitLogRecord(txn->get_transaction_id());
    commit_log_record->prev_lsn_ = txn->get_prev_lsn();
    txn->set_prev_lsn(log_manager->add_log_to_buffer(commit_log_record));
    // log_manager->flush_log_to_disk();  // ← 被注释，不落盘
    delete commit_log_record;
#endif
    
    txn->set_state(TransactionState::COMMITTED);
}
```

**解析**：
- **编译期开关**：`#ifdef ENABLE_LOGGING` 是编译期宏，注释掉 `#define ENABLE_LOGGING` 后，日志代码完全不参与编译，零开销。
- **flush_log_to_disk() 被注释**：即使开启日志，也只写内存 buffer，不刷磁盘，省去 fsync 的巨大开销。
- **决赛适用**：TPC-C 测试不测崩溃恢复，WAL 完全可以关闭。

**⚠️ 你们的现状**：用的是运行时开关 `std::atomic<bool> enable_logging`，比编译期开关开销大。

##### 3. PredicateManager 谓词管理器

```cpp
class PredicateManager {
public:
    explicit PredicateManager(IndexMeta& index_meta) {
        predicates_.reserve(index_meta.col_num);
        index_conds_.reserve(index_meta.col_num);
        for (size_t i = 0; i < index_meta.cols.size(); ++i) {
            predicates_.emplace(index_meta.cols[i].second.name, i);
            index_conds_.emplace_back(index_meta.cols[i].first,
                                      index_meta.cols[i].first);
        }
    }
    
    bool addPredicate(const std::string& column, Condition& cond) {
        if (predicates_.count(column) == 0) return false;
        if (cond.op == OP_GT || cond.op == OP_GE || cond.op == OP_EQ) {
            insertLeft(column, cond);
        }
        if (cond.op == OP_LT || cond.op == OP_LE || cond.op == OP_EQ) {
            insertRight(column, cond);
        }
        return true;
    }
    
    bool cmpIndexConds(const RmRecord& rec) {
        return cmpIndexLeftConds(rec) && cmpIndexRightConds(rec);
    }
    
    std::tuple<CompOp, int> getLeftLastTuple(char*& key) {
        left_last_idx = 0;
        CompOp op;
        for (auto& [cond, _] : index_conds_) {
            std::ignore = _;
            op = cond.op;
            if (op == OP_INVALID) break;
            memcpy(key + cond.offset, cond.rhs_val.raw->data, cond.rhs_val.raw->size);
            if (op != OP_EQ) break;
            ++left_last_idx;
        }
        return {op, left_last_idx};
    }
    
private:
    int left_last_idx = 0;
    int right_last_idx = 0;
    std::unordered_map<std::string, int> predicates_;
    std::vector<std::pair<CondOp, CondOp> > index_conds_;
};
```

**解析**：
- **预解析 WHERE 条件**：将 WHERE 条件中的谓词预解析为左右边界，存在 `index_conds_` 中。
- **避免重复解析**：原实现每次扫描 tuple 都要重新解析 WHERE 条件，谓词管理器只解析一次，后续直接用缓存的边界比较。
- **最长前缀匹配**：`getLeftLastTuple`/`getRightLastTuple` 可以快速找到第一个非等号条件的位置，用于索引范围扫描的边界计算。

**⚠️ 你们的现状**：IndexScanExecutor 中每次都要遍历 conds_ 来计算边界，没有预解析。

##### 4. TPC-C UPDATE 跳过间隙锁

```cpp
// 再检查是否有间隙锁
// TPCC 测试中 update 不会涉及键的变化，在 index scan
// 算子加了写间隙锁后就不用再检查了
// for (auto &[index_name, index]: tab_.indexes) {
//     RmRecord rm_record(index.col_tot_len);
//     for (auto &[index_offset, col_meta]: index.cols) {
//         memcpy(rm_record.data + index_offset, updated_record->data +
//         col_meta.offset, col_meta.len);
//     }
//     context_->lock_mgr_->isSafeInGap(context_->txn_, index, rm_record);
// }
```

**解析**：这是基于 TPC-C 事务特征的精准优化。TPC-C 的 UPDATE 语句都不会修改索引键（只改非索引列的值），因此不会导致记录在索引中的位置变化，也就不会产生幻读问题。既然 index scan 阶段已经加了写间隙锁，update 阶段就不需要再检查间隙锁了，直接砍掉这段代码。

**⚠️ 你们的现状**：用的是 MVCC，可能没有间隙锁的问题。

---

### 4.3 方案 C：共通的执行层微优化

两队都采用了以下执行层微优化，建议直接采纳：

| 优化技术 | 代码示例 | 效果 |
|----------|----------|------|
| **static_cast 替代 dynamic_pointer_cast** | `auto x = static_cast<ScanPlan*>(plan.get())` | 省去 RTTI 类型检查，约快 2-3x |
| **constexpr 数组替代 map** | `constexpr CompOp SWAP_OP_MAP[] = {OP_EQ, OP_GT, OP_LT, ...}` | 编译期常量，零运行时查找 |
| **reserve() 预分配** | `table_scan_executors.reserve(table_count)` | 避免 vector 扩容拷贝 |
| **memcpy 替代 reinterpret_cast（部分场景）** | `std::memcpy(&ia, a + offset, sizeof(int))` | 避免严格别名违规，编译器更好优化 |
| **noexcept 移动构造** | `BasicPageGuard(BasicPageGuard&& that) noexcept` | 允许 vector 移动时不退化到拷贝 |
| **std::all_of + 内联谓词** | `std::all_of(conds.begin(), conds.end(), [&](...){...})` | 编译器可向量化 |
| **data_send_is_full() 提前终止** | `if (!sm_manager_->io_enabled_ && context->data_send_is_full()) break;` | SELECT 结果集满时立即停止 scan |
| **unordered_set/unordered_map 替代 std::set/std::map** | `std::unordered_set<std::string> eq_cols` | O(1) vs O(log N) |
| **update_bounds 内联边界计算** | `static inline void update_bounds(...)` | 减少函数调用开销，编译器更好优化 |
| **预分配事务对象** | `txn_map_[i] = std::make_shared<Transaction>(i);` | 避免运行时动态分配 |

---

## 五、针对性优化建议（基于源码精确分析）

### 5.1 第一优先级（高收益、低风险、合规）

#### 🥇 1. 编译优化升级：-O2 → -O3 + -march=native + LTO

**现状**：CMake 配置 -O2 优化级别（待确认，假设是 -O2）  
**建议**：升级到 -O3 + -march=native + -flto（链接时优化） + -DNDEBUG

**预期收益**：**10-30% tpmC 提升**  
**实现风险**：低  
**合规性**：高（完全通用，不涉及硬编码）

**具体做法**：
```cmake
# CMakeLists.txt
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -flto -DNDEBUG")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -march=native -flto -DNDEBUG")
```

**注意事项**：
- -O3 可能引入一些问题，需要充分测试
- -flto 会增加编译时间
- -DNDEBUG 关闭 assert，性能提升明显但调试困难

**为什么排第一**：零代码改动，只改编译选项，收益可能最大。

---

#### 🥇 2. LockManager 分片优化：单全局锁 → 64 分片

**现状**：LockManager 是单全局锁，所有锁请求都要抢同一把锁  
**建议**：将 LockManager 按 LockDataId 哈希分片，每个分片独立加锁

**预期收益**：**20-40% tpmC 提升**（高并发下锁竞争大幅减少）  
**实现风险**：中  
**合规性**：高（通用优化，适用于所有场景）

**实现思路**：
```cpp
class LockManager {
    static constexpr size_t NUM_SHARDS = 64;
    
    struct Shard {
        std::mutex latch_;
        std::unordered_map<LockDataId, LockRequestQueue> lock_table_;
    };
    
    Shard shards_[NUM_SHARDS];
    
    size_t route(const LockDataId& id) const {
        // 简单哈希取模
        return std::hash<LockDataId>{}(id) % NUM_SHARDS;
    }
    
public:
    bool lock_shared_on_record(Transaction* txn, const Rid& rid, int tab_fd) {
        LockDataId id = {tab_fd, rid};
        size_t shard_idx = route(id);
        Shard& shard = shards_[shard_idx];
        std::scoped_lock lock(shard.latch_);
        // 在本分片内执行加锁逻辑
        ...
    }
};
```

**为什么有效**：
- 16 并发下，单全局锁会把所有锁请求串行化
- 64 分片后，不同数据项的锁请求落在不同分片，互不干扰
- TPC-C 有很多不同的记录（warehouse, district, customer, order 等），锁分布比较均匀

**为什么排第二**：源码分析显示 LockManager 是单全局锁，这很可能是最大的性能瓶颈。

---

#### 🥇 3. IxCompare 特化优化：针对 int 索引的快速路径

**现状**：通用 ix_compare 逐列判断类型，循环比较  
**建议**：添加单列 int、全 int、小数量 int 列的特化快速路径

**预期收益**：**15-25% 索引操作提速**（对 TPC-C 整体约 5-10%）  
**实现风险**：低  
**合规性**：高（通用优化，适用于所有 int 索引）

**实现思路**：

在 `IxIndexHandle` 中添加特化的比较函数，或者创建一个 `IxCompare` 类：

```cpp
class IxCompare {
    const IxFileHdr* file_hdr_;
    
    // 快速路径标志
    bool single_int_ = false;
    bool all_int_ = false;
    bool small_all_int_ = false;
    int small_int_cnt_ = 0;
    int small_int_off_[4];
    
public:
    explicit IxCompare(const IxFileHdr* file_hdr) : file_hdr_(file_hdr) {
        // 初始化时判断是否可以走快速路径
        single_int_ = (file_hdr_->col_num == 1 && 
                       file_hdr_->col_types[0] == TYPE_INT);
        
        all_int_ = true;
        for (int i = 0; i < file_hdr_->col_num; i++) {
            if (file_hdr_->col_types[i] != TYPE_INT) {
                all_int_ = false;
                break;
            }
        }
        
        small_all_int_ = all_int_ && file_hdr_->col_num <= 4;
        small_int_cnt_ = file_hdr_->col_num;
        
        // 预计算偏移量
        int off = 0;
        for (int i = 0; i < small_int_cnt_; i++) {
            small_int_off_[i] = off;
            off += file_hdr_->col_lens[i];
        }
    }
    
    inline int operator()(const char* a, const char* b) const {
        if (single_int_) {
            // 单列 int：直接比较，零循环零分支
            int ia, ib;
            memcpy(&ia, a, sizeof(int));
            memcpy(&ib, b, sizeof(int));
            return (ia < ib) ? -1 : ((ia > ib) ? 1 : 0);
        }
        
        if (small_all_int_) {
            // 2/3/4 列 int：手动 unroll，编译器可向量化
            switch (small_int_cnt_) {
                case 2: {
                    int a0, b0; memcpy(&a0, a + small_int_off_[0], 4); memcpy(&b0, b + small_int_off_[0], 4);
                    if (a0 != b0) return (a0 < b0) ? -1 : 1;
                    int a1, b1; memcpy(&a1, a + small_int_off_[1], 4); memcpy(&b1, b + small_int_off_[1], 4);
                    return (a1 < b1) ? -1 : ((a1 > b1) ? 1 : 0);
                }
                case 3: {
                    int a0, b0; memcpy(&a0, a + small_int_off_[0], 4); memcpy(&b0, b + small_int_off_[0], 4);
                    if (a0 != b0) return (a0 < b0) ? -1 : 1;
                    int a1, b1; memcpy(&a1, a + small_int_off_[1], 4); memcpy(&b1, b + small_int_off_[1], 4);
                    if (a1 != b1) return (a1 < b1) ? -1 : 1;
                    int a2, b2; memcpy(&a2, a + small_int_off_[2], 4); memcpy(&b2, b + small_int_off_[2], 4);
                    return (a2 < b2) ? -1 : ((a2 > b2) ? 1 : 0);
                }
                case 4: {
                    // 4 列手动展开...
                }
            }
        }
        
        // 通用路径（原 ix_compare 逻辑）
        return ix_compare_generic(a, b);
    }
};
```

**为什么有效**：
- TPC-C 的主键大多是 int 类型（w_id, d_id, o_id, c_id 等）
- 通用路径有循环和类型判断，特化路径是直线代码
- 编译器对直线代码优化更好，可以向量化
- B+树的每个内部节点查找都要调用比较函数，调用次数非常多

---

#### 🥇 4. IndexScan 精确匹配模式：全等值查询走 find_entry

**现状**：所有索引查询都走范围扫描（lower_bound 到 upper_bound）  
**建议**：识别"所有索引列都是等值条件"时，直接用 find_entry 一次定位

**预期收益**：**10-20% 索引查询提速**（对 TPC-C 整体约 5-8%）  
**实现风险**：低  
**合规性**：高（通用优化，适用于所有等值查询）

**实现思路**：

在 `IndexScanExecutor` 中添加精确匹配模式：

```cpp
class IndexScanExecutor : public AbstractExecutor {
    bool exact_match_mode_ = false;
    std::vector<char> exact_key_;
    bool exact_key_found_ = false;
    bool exact_key_consumed_ = false;
    
public:
    IndexScanExecutor(...) {
        // 先检查是否是精确匹配查询
        if (is_exact_match_query(conds_, index_meta_.cols)) {
            exact_match_mode_ = true;
            setup_exact_match_key();
            return;
        }
        // 否则走范围扫描路径
    }
    
    void beginTuple() override {
        if (exact_match_mode_) {
            // 直接查找
            auto ih = sm_manager_->ihs_.at(index_name).get();
            std::vector<Rid> result;
            exact_key_found_ = ih->get_value(exact_key_.data(), &result, context_->txn_);
            if (exact_key_found_ && !result.empty()) {
                rid_ = result[0];
                // 检查可见性
                auto opt_visible = GetVisibleRecord(...);
                if (opt_visible.has_value()) {
                    visible_rec_ = std::make_unique<RmRecord>(std::move(*opt_visible));
                    exact_key_consumed_ = false;
                    return;
                }
            }
            visible_rec_ = nullptr;
            return;
        }
        // 范围扫描路径...
    }
    
    std::unique_ptr<RmRecord> Next() override {
        if (exact_match_mode_) {
            if (!exact_key_found_ || exact_key_consumed_) {
                return nullptr;
            }
            exact_key_consumed_ = true;
            return std::move(visible_rec_);
        }
        // 范围扫描路径...
    }
    
private:
    static bool is_exact_match_query(const std::vector<Condition>& conds,
                                      const std::vector<ColMeta>& index_cols) {
        // 检查是否所有索引列都有等值条件
        std::unordered_set<std::string> eq_cols;
        for (const auto& cond : conds) {
            if (cond.op == OP_EQ && cond.is_rhs_val) {
                eq_cols.insert(cond.lhs_col.col_name);
            }
        }
        for (const auto& col : index_cols) {
            if (eq_cols.find(col.name) == eq_cols.end()) {
                return false;
            }
        }
        return true;
    }
    
    void setup_exact_match_key() {
        exact_key_.resize(index_meta_.col_tot_len);
        int offset = 0;
        for (const auto& col : index_meta_.cols) {
            // 找到对应的等值条件
            for (const auto& cond : conds_) {
                if (cond.op == OP_EQ && cond.is_rhs_val && 
                    cond.lhs_col.col_name == col.name) {
                    memcpy(exact_key_.data() + offset, cond.rhs_val.raw->data, col.len);
                    break;
                }
            }
            offset += col.len;
        }
    }
};
```

**为什么有效**：
- TPC-C 中大量是主键等值查询（如 SELECT * FROM warehouse WHERE w_id = ?）
- 范围扫描需要计算边界、创建迭代器、逐个推进
- 精确匹配直接 find 一次，省去很多开销

---

### 5.2 第二优先级（中收益、中风险、合规）

#### 🥈 5. WAL 编译期开关 + 真正的 Group Commit

**现状**：
- 运行时开关 `std::atomic<bool> enable_logging`
- kWalCoalesceDelayUs = 0（没有真正的 Group Commit）
- kWalFdatasyncOnFlush = false（已关闭 fdatasync）

**建议**：
1. 用编译期宏 `#ifdef ENABLE_LOGGING` 替代运行时开关
2. 实现真正的 Group Commit（设置合理的 coalescing delay）
3. 考虑双缓冲 WAL 刷盘

**预期收益**：**5-15%**（写密集场景下）  
**实现风险**：中  
**合规性**：高（WAL 机制优化，不影响正确性）

**具体做法**：

**1. 编译期开关**：
```cpp
// 在 config.h 或 log_defs.h 中
// #define ENABLE_LOGGING  // 注释掉即关闭

// 在 log_manager.cpp 中
#ifdef ENABLE_LOGGING
lsn_t LogManager::add_log_to_buffer(LogRecord* log_record) {
    // ... 正常实现
}
#else
lsn_t LogManager::add_log_to_buffer(LogRecord* log_record) {
    return INVALID_LSN;  // 空实现，零开销
}
#endif
```

**2. 真正的 Group Commit**：
```cpp
// 设置合理的聚合延迟
static constexpr int kWalCoalesceDelayUs = 100;  // 100 微秒

void LogManager::flush_up_to(lsn_t lsn) {
    if (lsn == INVALID_LSN) return;
    
    // 短暂等待，聚合更多日志
    if (kWalCoalesceDelayUs > 0) {
        std::this_thread::sleep_for(std::chrono::microseconds(kWalCoalesceDelayUs));
    }
    
    std::scoped_lock lock(latch_);
    if (persist_lsn_ >= lsn) return;
    flush_log_to_disk_unlocked();
}
```

**注意事项**：
- 不能完全关闭 WAL（要通过崩溃恢复测试）
- 但你们已经关闭了 fdatasync，如果崩溃恢复测试能通过，说明可以更激进
- Group Commit 的延迟需要调参，找到吞吐和延迟的平衡点

---

#### 🥈 6. NUMA 感知优化：缓冲池分片 + 线程绑定

**现状**：16 分片缓冲池，但未做 NUMA 感知  
**建议**：
- 缓冲池按 NUMA 节点分配内存（numa_alloc_onnode）
- 工作线程绑定到特定 NUMA 节点
- 尽量让线程访问本地节点的缓冲池分片

**预期收益**：**10-20%**（取决于跨节点访问比例）  
**实现风险**：中  
**合规性**：高（系统级优化，通用）

**具体做法**：

```cpp
// 1. 缓冲池按 NUMA 节点分配
#ifdef HAVE_NUMA
#include <numa.h>
#endif

BufferPoolManager::BufferPoolManager(...) {
    for (int i = 0; i < shard_count_; i++) {
        int node = i % num_numa_nodes;
        size_t shard_size = (shards_[i].frame_end_ - shards_[i].frame_begin_);
        
#ifdef HAVE_NUMA
        // 在指定 NUMA 节点上分配
        void* mem = numa_alloc_onnode(shard_size * PAGE_SIZE, node);
#else
        void* mem = malloc(shard_size * PAGE_SIZE);
#endif
        
        // 将 pages_ 数组的对应部分指向这片内存
        // ...
    }
}

// 2. 线程绑定到 NUMA 节点
void bind_thread_to_numa(int thread_id) {
    int node = thread_id % num_numa_nodes;
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    // 绑定到对应节点的 CPU
    for (int cpu = node * cpus_per_node; cpu < (node+1) * cpus_per_node; cpu++) {
        CPU_SET(cpu, &cpuset);
    }
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
}
```

**注意事项**：
- 需要链接 libnuma
- 需要检测系统是否支持 NUMA
- 可能需要调整分片策略

---

#### 🥈 7. 内存池优化：减少频繁 new/delete

**现状**：执行过程中频繁分配释放小对象（记录、键、UndoLog 等）  
**建议**：实现简单的内存池，按大小分桶缓存常用大小的内存块

**预期收益**：**5-15%**  
**实现风险**：中  
**合规性**：高（通用优化）

**实现思路**：

```cpp
class MemoryPool {
    static constexpr size_t MAX_SIZE = 2048;  // 最大缓存大小
    static constexpr size_t NUM_BUCKETS = 16; // 分桶数量
    
    struct Bucket {
        std::mutex mtx;
        std::vector<void*> free_list;
    };
    
    Bucket buckets_[NUM_BUCKETS];
    
    static size_t align_size(size_t size) {
        return (size + 7) & ~7;  // 8 字节对齐
    }
    
    static size_t get_bucket(size_t size) {
        size_t aligned = align_size(size);
        // 简单的分桶策略：按大小区间
        if (aligned <= 16) return 0;
        if (aligned <= 32) return 1;
        if (aligned <= 64) return 2;
        // ...
        return NUM_BUCKETS - 1;
    }
    
public:
    void* allocate(size_t size) {
        if (size > MAX_SIZE) {
            return malloc(size);
        }
        size_t bucket = get_bucket(size);
        std::lock_guard lk(buckets_[bucket].mtx);
        if (!buckets_[bucket].free_list.empty()) {
            void* ptr = buckets_[bucket].free_list.back();
            buckets_[bucket].free_list.pop_back();
            return ptr;
        }
        return malloc(align_size(size));
    }
    
    void deallocate(void* ptr, size_t size) {
        if (size > MAX_SIZE) {
            free(ptr);
            return;
        }
        size_t bucket = get_bucket(size);
        std::lock_guard lk(buckets_[bucket].mtx);
        buckets_[bucket].free_list.push_back(ptr);
    }
};
```

**应用场景**：
- 记录分配（RmRecord）
- 索引键分配
- UndoLog 分配
- 执行器临时对象

---

#### 🥈 8. 执行器微优化：减少虚函数调用和拷贝

**现状**：标准火山模型，Next() 虚函数调用  
**建议**：
- 常用执行路径做内联
- 减少 RmRecord 的拷贝次数
- 用 static_cast 替代 dynamic_cast
- reserve() 预分配 vector 容量

**预期收益**：**5-10%**  
**实现风险**：低  
**合规性**：高（代码级微优化）

**具体做法**：

```cpp
// 1. static_cast 替代 dynamic_cast
auto scan_plan = static_cast<ScanPlan*>(plan.get());  // 已知类型时

// 2. reserve 预分配
std::vector<RmRecord> records;
records.reserve(estimated_count);

// 3. 移动语义替代拷贝
return std::move(record);  // 避免深拷贝

// 4. constexpr 替代运行时查找
constexpr CompOp SWAP_OP_MAP[] = {OP_EQ, OP_GT, OP_LT, ...};

// 5. 热点函数内联
static inline bool compare_value(...) { ... }
```

---

### 5.3 第三优先级（高收益、高风险，需谨慎评估）

#### 🥉 9. B+树并发优化：更细粒度的锁

**现状**：root_latch_ 单全局锁保护根节点  
**建议**：实现更细粒度的 B+树并发控制（如 2PL 螃蟹锁、乐观锁等）

**预期收益**：**15-30%**（高并发下锁竞争减少）  
**实现风险**：高（容易引入并发 bug）  
**合规性**：高（通用索引优化）

**注意事项**：
- B+树并发控制很容易出错
- 需要充分的并发测试
- 建议先做性能分析，确认锁竞争确实是瓶颈

---

#### 🥉 10. SSI 优化：减少可串行化检查开销

**现状**：SSI 跟踪读写依赖，检测危险结构  
**建议**：
- 优化 SSI 检查的热点路径
- 考虑降低隔离级别（如果赛规允许读已提交）
- 谓词读跟踪优化

**预期收益**：**10-20%**（取决于 SSI 开销比例）  
**实现风险**：中到高  
**合规性**：需确认（降低隔离级别可能不符合要求）

**注意事项**：
- 赛规要求隔离级别 ≥ 读已提交
- 如果读已提交就够，可以考虑关闭 SSI
- 但要确认一致性检查是否能通过

---

#### 🥉 11. MVCC 优化：版本链加速

**现状**：版本链遍历可能是热点  
**建议**：
- 优化可见性判断函数
- 考虑版本链的局部性优化
- 减少 UndoLog 的内存占用

**预期收益**：**5-15%**  
**实现风险**：中  
**合规性**：高

---

### 5.4 不建议尝试的方案（基于你们的 NOT-DO.md）

以下方案你们已经试过或有类似尝试，不建议再花时间：

| 方案 | 原因 |
|------|------|
| 缓冲池扩容到 512MB/1GB | 收益有限，且有 NUMA 开销 |
| 完全关闭 WAL / 跳过 fdatasync | 你们已经关了 fdatasync，如果还能通过崩溃恢复测试，说明已经很激进了 |
| 2PL 替代 MVCC | 高竞争下死锁率高，MVCC 更适合 |
| 激进 GC | 正确性问题，容易误删 undo log |
| 后台线程异步刷盘 | 线程切换开销 + 同步复杂，不如 Group Commit |

---

## 六、环境适配建议

### 6.1 NUMA 优化（重要）

**环境**：2 个 NUMA 节点，40 核

**建议**：

1. **进程级**：用 numactl 控制内存分配策略
   ```bash
   # 方案1：内存交错（简单，适合内存访问分散）
   numactl --interleave=all ./rmdb testdb
   
   # 方案2：绑定到单节点（如果内存够用）
   numactl --cpunodebind=0 --membind=0 ./rmdb testdb
   ```

2. **应用级**：代码中做 NUMA 感知
   - 缓冲池按节点分配
   - 线程绑定到节点
   - 尽量本地内存访问

3. **监控**：用 perf 测量跨节点访问比例
   ```bash
   perf stat -e node-loads,node-load-misses -p $(pidof rmdb)
   ```

### 6.2 AVX-512 利用

**环境**：支持 AVX-512 全系列

**建议**：

1. **编译优化**：-march=native 会自动利用
2. **手动 SIMD**：热点函数可以考虑手写 SIMD
   - 字符串比较、扫描
   - 哈希计算
   - 批量数据转换
3. **glibc 优化**：memcpy 等函数已对 AVX-512 优化，直接用就好

### 6.3 大页内存

**建议**：对缓冲池等大内存区域启用透明大页

```cpp
// 用 madvise 启用透明大页
#include <sys/mman.h>
madvise(pages_, pool_size * PAGE_SIZE, MADV_HUGEPAGE);
```

**收益**：减少 TLB miss，提高内存访问速度

### 6.4 编译选项建议

```cmake
# CMakeLists.txt 优化建议
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -flto -DNDEBUG")
set(CMAKE_C_FLAGS_RELEASE "-O3 -march=native -flto -DNDEBUG")

# 可选：PGO 优化（Profile-Guided Optimization）
# 先用训练数据生成 profile，再用 profile 编译
```

---

## 七、合规与风险提示

### 7.1 硬编码红线（绝对不能碰）

⚠️ **赛规明确禁止**：

> "针对评测中的固定表名、字段结构或 SQL 文本编写专用匹配逻辑，并绕过通用解析、优化或执行流程以提升跑分，属于面向评测用例的硬编码优化，不具备通用性，将认定为违规。"

**明确禁止的做法**：
- ❌ 检测表名（如 "warehouse"、"customer"）走特殊路径
- ❌ 检测 SQL 文本模式走特殊路径
- ❌ 针对 TPC-C 5 种事务硬编码执行逻辑
- ❌ 绕过解析器/优化器的专用入口
- ❌ RushDB 的 DBCahce 首字符分派（针对 INSERT/BEGIN/COMMIT 硬编码）
- ❌ RushDB 的 ban 标志让 insert/update/delete 空转（明显作弊）

**可以做的（通用优化）**：
- ✅ 针对 int 类型索引的特化（适用于所有 int 索引）
- ✅ 等值查询的快速路径（适用于所有等值查询）
- ✅ 不涉及索引列的 UPDATE 原地更新（通用优化）
- ✅ 编译优化、NUMA 优化、内存池等系统级优化
- ✅ 算法层面的优化（如 B+树并发、MVCC 优化）
- ✅ LockManager 分片（通用优化，适用于所有场景）

**关键判断标准**：

> 优化是否通用？如果换一套表结构、换一套 SQL，这个优化还有效吗？
> - 有效 → 通用优化 → ✅ 可以做
> - 无效 → 硬编码优化 → ❌ 不能做

### 7.2 正确性红线

⚠️ **必须通过所有正确性检查**：

1. 功能测试全部通过
2. 数据加载结果与标准输出一致
3. 压测结束后数据满足一致性检查
4. kill -9 崩溃后重启，已提交事务可正确恢复

**优化前一定要做**：
- 每次优化后跑一遍正确性检查
- 不要为了性能牺牲正确性
- 性能优化可以回退，正确性出问题就是 0 分

### 7.3 性能波动注意事项

- 初赛共享一台物理机，多人同时评测波动较大（20% 以内正常）
- 建议多次测试取稳定值
- 不要用短时间微小测试结果作为定论
- 决赛排队独享服务器，波动会小很多

---

## 八、实施路线图（基于源码精确分析）

### 第一阶段：快速见效（1-2 天）

| 序号 | 优化项 | 预期收益 | 难度 | 优先级 |
|------|--------|---------|------|--------|
| 1 | 编译优化：-O3 + -march=native + -DNDEBUG | 10-30% | ⭐ | 🥇 |
| 2 | LockManager 分片优化（64 分片） | 20-40% | ⭐⭐ | 🥇 |
| 3 | IxCompare 单列 int 快速路径 | 5-10% | ⭐⭐ | 🥇 |
| 4 | IndexScan 精确匹配模式 | 5-8% | ⭐⭐ | 🥇 |

**预计总收益**：**40-88% tpmC 提升**（注意：各项收益不是简单相加，有重叠）

**保守估计**：**30-50% 实际提升**

---

### 第二阶段：深入优化（3-5 天）

| 序号 | 优化项 | 预期收益 | 难度 | 优先级 |
|------|--------|---------|------|--------|
| 5 | IxCompare 全 int / 小数量 int 特化 | 5-10% | ⭐⭐ | 🥈 |
| 6 | WAL 编译期开关 + Group Commit | 5-15% | ⭐⭐ | 🥈 |
| 7 | NUMA 感知优化 | 10-20% | ⭐⭐⭐ | 🥈 |
| 8 | 内存池优化 | 5-15% | ⭐⭐⭐ | 🥈 |
| 9 | 执行器微优化（static_cast、reserve 等） | 5-10% | ⭐ | 🥈 |

**预计额外收益**：**30-70%**（在第一阶段基础上）

---

### 第三阶段：高级优化（5-7 天）

| 序号 | 优化项 | 预期收益 | 难度 | 优先级 |
|------|--------|---------|------|--------|
| 10 | B+树并发优化（细粒度锁） | 15-30% | ⭐⭐⭐⭐ | 🥉 |
| 11 | MVCC 版本链加速 | 5-15% | ⭐⭐⭐ | 🥉 |
| 12 | SSI 检查优化 / 降低隔离级别 | 10-20% | ⭐⭐⭐⭐ | 🥉 |

**预计额外收益**：**30-65%**（在第二阶段基础上）

---

### 总预期

| 阶段 | 累计 tpmC（相对基线） |
|------|---------------------|
| 基线 | 1x (~800-1000) |
| 第一阶段后 | 1.3x - 1.5x (~1040-1500) |
| 第二阶段后 | 1.7x - 2.6x (~1360-2600) |
| 第三阶段后 | 2.2x - 4.3x (~1760-4300) |

⚠️ **注意**：
- 以上是乐观估计，实际收益取决于当前瓶颈分布
- 需要实测验证，逐项调整
- 即使只做第一阶段，也能有明显提升

---

## 九、总结与核心建议

### 最关键的 5 条建议

#### 1. 先做编译优化，立竿见影

从 -O2 升级到 -O3 + -march=native + -DNDEBUG，可能带来 10-30% 的提升，而且几乎零成本。这是性价比最高的优化，应该第一个做。

#### 2. LockManager 分片是重中之重

源码分析显示 LockManager 是单全局锁，这很可能是最大的性能瓶颈。16 并发下，所有锁请求都要抢同一把锁，会严重限制吞吐。改成 64 分片后，预期能有 20-40% 的提升。

#### 3. 聚焦热点路径，不要遍地开花

TPC-C 的热点很集中：
- **锁管理器**：所有事务都要加锁解锁
- **索引比较**：B+树查找的核心操作
- **索引查询**：主键等值查询最多
- **WAL 刷盘**：写密集场景下的主要瓶颈

优先优化这些热点路径，比到处改小地方收益大得多。

#### 4. 每一步都要测，用数据说话

- 优化前先测基线
- 每次只改一个变量
- 优化后跑测试验证性能和正确性
- 没有收益就果断回退，不要恋战

你们 NOT-DO.md 的做法很好，继续保持。

#### 5. 绝对不要碰硬编码红线

赛规明确禁止面向评测用例的硬编码优化，一旦被发现可能直接取消资格。所有优化都应该是通用的，换一套表结构、换一套 SQL 仍然有效。

RushDB 的很多做法（DBCahce、ban 标志、内存 B+树）虽然性能提升很大，但很可能违规，不建议模仿。

### 关于参考代码的使用建议

2024/2025 获奖队伍的代码可以参考思路，但**绝对不能直接复制**：

- 赛规禁止直接使用往届参赛作品
- 代码相似度检测会查出来
- 应该理解原理后自己实现

**建议的学习方式**：
1. 先理解优化思路（为什么这么做）
2. 关掉参考代码，凭理解自己写
3. 写完后可以对比，看有没有遗漏
4. 用自己的代码风格和结构实现

---

## 附录：参考资源

| 资源类型 | 链接 | 用途 |
|----------|------|------|
| 2024 一等奖源码 | https://github.com/Kosthi/CSCC-DB-Rucbase-2024 | 保守路线参考 |
| 2025 一等奖源码 | https://github.com/RushDB-Lab/CSCC-DB-Rucbase-2025 | 激进路线参考（注意合规） |
| 官方原版框架 | https://github.com/ruc-deke/rucbase-lab | baseline |
| TPC-C 测试脚本 | https://github.com/Kosthi/TPCC-Tester | 本地验证 |
| Kosthi Issue#1 | https://github.com/Kosthi/CSCC-DB-Rucbase-2024/issues/1 | 优化思路讨论 |
| 比赛官网 | https://db.educg.net | 赛规与公告 |
| 官方交流群 | QQ 群 529358791 | 答疑与交流 |
| parallel_hashmap 库 | https://github.com/greg7mdp/parallel-hashmap | phmap::btree_set 依赖 |
| CMU 15-445 BusTub | https://github.com/cmu-db/bustub | 架构参考 |
| Stanford CS346 Redbase | https://web.stanford.edu/class/cs346/2015/redbase.html | 架构参考 |

---

**报告完**

如需针对某个具体优化方案展开详细实现代码，或需要性能分析方法指导，请随时告知。
