# 数据库管理系统设计赛 — Rucbase/RMDB 实战性能提升方法论

> **场景定位**：全国大学生计算机系统能力大赛 - 数据库管理系统设计赛
> **框架**：Rucbase（人大卢卫教授团队开发，参考 CMU BusTub + Stanford Redbase）
> **评测形式**：初赛 10 道功能题（正确性）+ 决赛 TPC-C 性能测试（吞吐量 tpmC）
> **历史基准**：2024 冠军 Kosthi/CSCC-DB-Rucbase-2024 跑到 8w tpmC 上限（2/325 一等奖）；2025 冠军 RushDB-Lab/CSCC-DB-Rucbase-2025 一等奖
> **文档目标**：在 3-6 个月内通过系统性优化把 TPC-C tpmC 提升到一等奖区间（不是写"最好的数据库"，是"在比赛中拿最高分"）

---

## 总序：比赛优化的思维切换

把"通用数据库优化方法论"和"比赛优化方法论"区分开，是这条路最重要的一步。两套思路的差异不是程度差异，是**目标函数差异**：

| 维度 | 通用数据库优化 | 比赛优化（你现在的场景） |
|------|--------------|----------------------|
| 目标函数 | 综合指标（吞吐+延迟+稳定性+正确性+可维护性） | **单一指标**：TPC-C tpmC（峰值吞吐） |
| 优化边界 | 不能牺牲正确性、可维护性、长期稳定性 | **可以牺牲**：可维护性、长期稳定性、抗故障性（只要 TPC-C 跑过正确性校验即可） |
| 时间窗口 | 长期演进 | 决赛固定时长，按周迭代 |
| 评判者 | 生产用户、SRE、DBA | 自动化 benchmark 脚本 |
| 反馈周期 | 慢、模糊 | 秒级、精确（tpmC 数字） |
| 优化方向 | 平衡各模块 | **倾斜**到 TPC-C 5 类事务的热点路径 |

**一句话总结**：通用优化是"补短板"，比赛优化是"加长板"。在 TPC-C 场景下，你需要把 95% 的精力投在 5% 的代码上——那 5% 是 TPC-C 事务每秒执行上万次的关键路径。

这份方法论围绕一个核心问题展开：**如何在有限时间内，把 Rucbase 的 TPC-C 性能从初始的几千 tpmC 推到 8 万 tpmC 一等奖区间**。

---

## 第一部分：Rucbase/RMDB 架构剖析与优化空间识别

### 1.1 Rucbase 项目结构（你必须先摸清的家底）

Rucbase 是一个教学用精简 RDBMS，代码量约 2-3 万行，模块边界清晰。从公开的 `RMDB项目结构` 文档和实验指导看，主要模块分布在：

```
src/
├── record/         # 记录存储组织（行存格式、定长/变长记录）
├── replacer/       # 缓冲区替换算法（LRU 实现）
├── storage/        # 文件存储管理（DiskManager、Page 抽象）
├── system/         # 元数据存储（catalog、schema）
├── index/          # B+ 树索引（ISAM、B+Tree）
├── concurrency/    # 锁管理器、事务管理器（2PL，可串行化）
├── recovery/       # WAL 日志、log manager
├── parser/         # SQL 解析
├── optimizer/      # 查询优化器（可能较简陋，rule-based 为主）
├── execution/      # 算子执行（火山模型或向量化）
└── network/        # 客户端协议（如 libpq 或自定义）
```

**第一周任务**：把每个模块的代码读一遍，重点理解：
1. **Page 的物理格式**：定长/变长记录如何存储？slot 目录如何组织？空闲空间如何管理？
2. **Buffer Pool 的替换算法**：默认是 LRU？还是 Clock？是否有 midpoint insertion？
3. **B+Tree 的并发控制**：crabbing protocol（latch coupling）还是 optimistic？
4. **锁管理器的数据结构**：lock table 用什么实现？锁等待队列如何管理？死锁检测是 timeout 还是 wait-for graph？
5. **WAL 的实现**：日志格式？fsync 频率？是否有 group commit？
6. **查询执行模型**：火山模型（next() 拉模型）还是物化模型？是否支持向量化？

**为什么这一步必须先做**：所有后续优化都建立在你对当前实现的精确认知之上。凭"教科书上的 PostgreSQL 是这样做的"去优化，会直接踩坑——Rucbase 的实现细节和 PostgreSQL 差很多。

### 1.2 Rucbase 默认实现的典型"性能债"

教学框架为了保证可读性，会在性能上做出明显牺牲。下面列出 Rucbase 默认实现中**最常见的性能债**，这是你的优化起点：

**性能债 1：粗粒度锁**
- 整个 buffer pool 用一把全局 mutex 保护
- 整个 lock manager 用一把全局 latch 保护
- B+Tree 遍历期间持有 root latch 不释放
- 事务 commit 时持有 transaction manager 全局锁

**性能债 2：低效替换算法**
- 纯 LRU 实现，没有 midpoint insertion，全表扫描会污染热数据
- 没有预读（read-ahead）机制
- 没有 write-behind 主动刷脏

**性能债 3：WAL 串行化**
- 每次 commit 都 fsync，没有 group commit
- log 写入用全局锁，所有事务串行排队
- 日志格式可能冗余（重复字段、未对齐）

**性能债 4：B+Tree 读写放大**
- 节点没有压缩
- 内部节点分裂/合并用全锁
- 范围扫描没有 prefetch
- 没有区分 leaf latch 和 internal latch

**性能债 5：查询执行低效**
- 火山模型每次 next() 都有虚函数调用
- 没有 expression compilation
- nested loop join 没有优化为 block nested loop 或 hash join
- 聚合算子没有 hash aggregation

**性能债 6：I/O 模型**
- 同步阻塞 I/O（read/write）
- 每次 I/O 一次 syscall
- 没有用 io_uring 或 AIO

**性能债 7：内存管理**
- 用标准 new/delete，没有内存池
- 字符串、临时对象频繁分配
- 没有 numa awareness

这 7 类性能债就是你接下来的 7 个优化战场。**初赛阶段你应该已经修复了"正确性"层面的实现 bug，决赛阶段的任务就是把这 7 类性能债逐个消除。**

### 1.3 优化空间识别的方法论

如何系统性地识别"还有哪些地方可以优化"？推荐 3 种方法并用：

**方法 A：perf 火焰图法**
```bash
# 在 TPC-C 压测期间采样
perf record -F 99 -p <db_pid> -g -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```
打开 flame.svg，**前 10 个最宽的栈**就是你最大的优化机会。典型 Rucbase 在 TPC-C 下的火焰图会显示：
- `LockManager::acquire_lock` 占 30-40% CPU
- `BufferPool::fetch_page` 占 15-20% CPU
- `LogManager::log_record` 占 10-15% CPU
- `BPlusTree::find_leaf` 占 10-15% CPU
- 其他（解析、优化、执行）合计 20-30%

**方法 B：syscall 直方图**
```bash
perf stat -e 'syscalls:sys_enter_*' -p <db_pid> -- sleep 30 2>&1 | grep -v "^$" | sort -k1 -nr | head -20
```
看哪些 syscall 调用最多。典型场景：`futex` > `read`/`write`/`fsync` > `mmap`/`munmap`。
- `futex` 高 → 锁竞争
- `fsync` 高 → WAL 串行化
- `read` 高 → buffer pool miss

**方法 C：延迟分布法**
在 TPC-C 客户端记录每类事务的延迟分布（P50/P90/P99/P999）：
- New-Order 延迟高 → 通常是锁竞争或 B+Tree 写入
- Payment 延迟高 → 通常是与 New-Order 共享热点的锁冲突
- Stock-Level 延迟高 → 通常是范围扫描或 buffer pool miss
- Order-Status 延迟高 → 通常是索引选择不当
- Delivery 延迟高 → 通常是行锁等待

**这 3 种方法必须每周做一次。**火焰图告诉你"CPU 在哪里烧"，syscall 告诉你"内核在哪里被消耗"，延迟分布告诉你"哪个事务被拖慢"。三者交叉验证才能定位真正的瓶颈。

---

## 第二部分：TPC-C 负载特征分析 — 你的"敌人"是谁

### 2.1 TPC-C 5 类事务的精确比例与瓶颈特征

TPC-C 是一个 OLTP 基准，模拟批发商订单处理系统。5 类事务的混合比例为：

| 事务类型 | 比例 | 平均 SQL 数 | 关键热点 | 主要瓶颈 |
|---------|------|-----------|---------|---------|
| New-Order | 45% | ~15-20 条 | WAREHOUSE、DISTRICT、CUSTOMER、ITEM、STOCK、ORDER | 锁竞争、WAL fsync |
| Payment | 43% | ~3-5 条 | WAREHOUSE、DISTRICT、CUSTOMER | 锁竞争（与 New-Order 共享 W/D 锁） |
| Order-Status | 4% | ~5 条 | CUSTOMER、ORDER、ORDER-LINE | 索引选择 |
| Delivery | 4% | ~10-15 条 | ORDER、CUSTOMER、ORDER-LINE | 行锁等待 |
| Stock-Level | 4% | ~5 条 | DISTRICT、ORDER-LINE、STOCK | 范围扫描、buffer pool miss |

**最关键的事实**：New-Order + Payment 占 88% 的事务量。**这两类事务的吞吐直接决定了你的 tpmC**。其他 3 类事务即使优化到极致，对总分的贡献也最多 12%。

**优化原则**：先优化 New-Order + Payment 路径，再考虑其他 3 类。

### 2.2 TPC-C 的热点行（Hotspot）分析

TPC-C 的设计**故意制造热点**，这是其与"真实负载"最大的不同：

**热点 1：WAREHOUSE 表的 W_ID 行**
- 每个 New-Order/Payment 事务都会 UPDATE WAREHOUSE SET W_YTD = W_YTD + ... WHERE W_ID = ?
- W_ID 是常数（每个 client 绑定一个 warehouse）
- **同一 warehouse 的所有事务在这行上串行排队**
- 这是 TPC-C 最大、最不可避免的热点

**热点 2：DISTRICT 表的 D_ID 行**
- 每个 New-Order 事务 UPDATE DISTRICT SET D_NEXT_O_ID = D_NEXT_O_ID + 1 WHERE D_ID = ? AND D_W_ID = ?
- D_NEXT_O_ID 是自增 ID
- 同一 district 的事务在这行上严格串行

**热点 3：CUSTOMER 表的 C_ID 行**
- Payment 事务 UPDATE CUSTOMER SET C_BALANCE = ... WHERE C_W_ID = ? AND C_D_ID = ? AND C_ID = ?
- C_ID 范围 [1, 3000]，分布相对均匀但仍有冲突

**热点 4：STOCK 表的 S_I_ID 行**
- New-Order 事务对每个订单项 UPDATE STOCK SET S_QUANTITY = ... WHERE S_I_ID = ? AND S_W_ID = ?
- 5-15 个订单项/事务，S_I_ID 分布相对均匀

**优化含义**：
- WAREHOUSE 和 DISTRICT 热点无法消除，**这是 TPC-C 设计的本质**
- 优化方向是：**让热点行的锁获取/释放尽可能快**（不优化锁本身，优化锁的"轻量化"）
- CUSTOMER 和 STOCK 的冲突可以通过 **MVCC + 乐观锁** 大幅缓解
- 锁管理器的实现质量决定上限

### 2.3 TPC-C 的 I/O 模式

| 操作 | I/O 模式 | 缓存友好度 |
|------|---------|-----------|
| 读 WAREHOUSE 行 | 点查，每次访问相同 W_ID | 极高（必命中 buffer pool） |
| 读 DISTRICT 行 | 点查，D_W_ID+D_ID | 极高 |
| 读 CUSTOMER 行 | 点查，C_ID 范围 1-3000 | 中（3000 行可能不全部驻留） |
| 读 ITEM 行 | 点查，I_ID 范围 1-100000 | 中（100K 行可能部分驻留） |
| 读/写 STOCK 行 | 点查，S_I_ID 范围 1-100000 | 中 |
| 写 ORDER 行 | 自增 ID，顺序追加 | 高 |
| 写 ORDER-LINE 行 | 自增 ID，顺序追加 | 高 |
| 写 HISTORY 行 | 顺序追加 | 高 |

**关键观察**：
- **大部分读操作集中在小范围热点数据上**，buffer pool 命中率应该 > 99%
- **写操作以追加为主**（ORDER、ORDER-LINE、HISTORY）
- **UPDATE 集中在 WAREHOUSE/DISTRICT/STOCK**，这才是真正的写瓶颈
- WAREHOUSE 总数少（10-1000 个），完全可以驻留内存
- DISTRICT 每个 W 10 个，更小
- CUSTOMER 每个 W 30000 个，10 个 W 就是 30 万行，也能驻留

**优化含义**：**buffer pool 设计得好，TPC-C 的读 I/O 几乎可以归零**。瓶颈会转移到锁、WAL、CPU 上。

### 2.4 TPC-C 的 CPU 与锁模式

TPC-C 是**典型的锁竞争型负载**，而非 CPU 计算密集型或 I/O 密集型。这一点决定了 90% 的优化方向：

- **不要先优化 CPU 算法复杂度**（B+Tree 的 O(log n) vs O(1) 在 TPC-C 下根本不是瓶颈）
- **要先优化锁竞争**（futex 系统调用、原子操作、无锁数据结构）
- **再优化 WAL 串行化**（group commit、异步 fsync）
- **最后优化 CPU 缓存友好性**（cacheline 对齐、false sharing）

**如果你看到 perf top 显示 `__lll_lock_wait` 或 `futex_wait` 排在前面，恭喜你，你的瓶颈在锁上——这是 TPC-C 最容易拿分的地方。**

---

## 第三部分：拿分点优先级矩阵（ROI 分析）

### 3.1 优化项 ROI 矩阵

下表是 Rucbase 上 TPC-C 优化的拿分点矩阵，按 ROI（投入回报比）排序。**ROI = 预期 tpmC 提升倍数 / 工程投入周数**：

| # | 优化项 | 预期提升 | 工程投入 | ROI | 难度 | 优先级 |
|---|-------|---------|---------|-----|------|-------|
| 1 | WAL Group Commit | 1.5-2x | 1 周 | 高 | 中 | P0 |
| 2 | 锁管理器 shard 化（去掉全局锁） | 1.3-1.5x | 1-2 周 | 高 | 中 | P0 |
| 3 | Buffer Pool 分片（多实例） | 1.2-1.3x | 1 周 | 高 | 低 | P0 |
| 4 | LRU → LRU-K / CLOCK 改造 | 1.1-1.2x | 3-5 天 | 中 | 低 | P0 |
| 5 | B+Tree 乐观锁（leaf latch crabbing） | 1.2-1.4x | 2 周 | 高 | 高 | P1 |
| 6 | MVCC 实现（替代 2PL 读锁） | 1.5-2x | 3-4 周 | 中 | 极高 | P1 |
| 7 | 算子向量化（批量 next） | 1.2-1.5x | 2-3 周 | 中 | 中 | P1 |
| 8 | Buffer Pool 预读（read-ahead） | 1.1-1.2x | 1 周 | 中 | 低 | P1 |
| 9 | log buffer 异步刷盘（双 buffer） | 1.1-1.15x | 1 周 | 中 | 低 | P1 |
| 10 | 内存池替代 new/delete | 1.1x | 1 周 | 中 | 低 | P2 |
| 11 | Group Commit + io_uring | 1.1-1.2x | 2 周 | 中 | 中 | P2 |
| 12 | CBO 优化器（替代 RBO） | 1.1-1.3x | 3-4 周 | 中 | 高 | P2 |
| 13 | Hash Join 实现 | 1.1-1.2x | 1 周 | 中 | 中 | P2 |
| 14 | 脏页异步刷盘（doublewrite 优化） | 1.05-1.1x | 1 周 | 中 | 中 | P2 |
| 15 | 行格式紧凑化（变长字段优化） | 1.05-1.1x | 1-2 周 | 中 | 中 | P3 |
| 16 | SQL 解析缓存（plan cache） | 1.05-1.1x | 1 周 | 中 | 低 | P3 |
| 17 | 表达式编译（codegen） | 1.1-1.2x | 4+ 周 | 低 | 极高 | P3 |
| 18 | NUMA-aware buffer pool | 1.05-1.1x | 2 周 | 低 | 高 | P3 |

### 3.2 阶段性优化路线图

按时间窗口分配优化任务：

**阶段 1：基础正确性 + 基线建立（1-2 周）**
- [ ] 完成 Rucbase 代码阅读，理解每个模块
- [ ] 跑通 TPC-C 正确性测试（10 个 warehouse 配置）
- [ ] 建立可重复 baseline（同一配置跑 3 次，tpmC 方差 < 5%）
- [ ] 用 perf 火焰图、off-cPU 火焰图、syscall 直方图记录初始瓶颈分布
- [ ] 记录 baseline 性能数字：tpmC、P99 latency、CPU 利用率、IOPS

**阶段 2：P0 高 ROI 优化（3-4 周）**
- [ ] WAL Group Commit（预期 +50-100% tpmC）
- [ ] 锁管理器分片化（预期 +30-50% tpmC）
- [ ] Buffer Pool 分片（预期 +20-30% tpmC）
- [ ] LRU → LRU-K 或 CLOCK（预期 +10-20% tpmC）
- [ ] 每个优化完成后立即对比 baseline，确认无回归

**阶段 3：P1 中 ROI 优化（4-6 周）**
- [ ] B+Tree 乐观锁（预期 +20-40% tpmC）
- [ ] MVCC 实现（如果赛题要求.Serializable 必须保留，考虑 MVCC+2PL 混合）
- [ ] 算子向量化（预期 +20-50% tpmC，主要影响 Order-Status/Stock-Level）
- [ ] Buffer Pool 预读
- [ ] log buffer 双 buffer 异步刷盘

**阶段 4：P2/P3 边界优化（2-3 周，决赛冲刺）**
- [ ] 内存池替代 new/delete
- [ ] CBO 优化器（如果时间允许）
- [ ] Hash Join 实现
- [ ] 脏页异步刷盘优化
- [ ] 行格式紧凑化
- [ ] SQL plan cache
- [ ] NUMA-aware（如果有 NUMA 服务器）

**阶段 5：决赛答辩准备（1 周）**
- [ ] 性能数据可视化（baseline → 各阶段 tpmC 增长曲线）
- [ ] 火焰图对比（before/after）
- [ ] 架构演进图
- [ ] 创新点提炼（3-5 个最有亮点的优化）
- [ ] 答辩 PPT + 演示视频

### 3.3 优化的"反向优先级"——不该先做的事

避免在以下事情上浪费时间：

**❌ 不要先做**：
- 实现完整的 SQL 优化器（CBO 投入大，TPC-C 查询模式简单，RBO 已经够用）
- 实现向量化执行引擎（除非已到 P0/P1 全部完成）
- 实现 codegen（LLVM/JIT 投入极大，TPC-C 收益有限）
- 重写存储引擎（B+Tree → LSM）（TPC-C 是读多写少场景，B+Tree 更合适）
- 支持分布式（TPC-C 决赛是单机）
- 支持 OLAP（TPC-H 不是你的比赛场景）

**❌ 不要做的"伪优化"**：
- 调大 buffer pool 而不分析命中率（如果命中率已经 99%，调大无收益）
- 增加 thread pool 大小而不消除锁竞争（线程数越多锁竞争越激烈）
- 加更多索引而不考虑写放大（TPC-C 写多，索引越多越慢）
- 启用 huge pages 而不验证 NUMA 影响（见 USENIX ATC 2014 论文）

---

## 第四部分：核心模块优化实战手册

### 4.1 Buffer Pool 优化

#### 4.1.1 Rucbase 默认实现的典型问题

Rucbase 的 Buffer Pool 默认实现通常有以下问题：
1. 单实例，单 LRU 链表，单 mutex
2. 纯 LRU，没有 midpoint insertion
3. 每次 fetch_page 都加全局锁
4. 没有 write-behind 主动刷脏
5. dirty page 在 evict 时才写盘，造成尾部延迟尖刺

#### 4.1.2 优化步骤（按 ROI 排序）

**步骤 1：分片化 Buffer Pool（预期 +20-30%）**

把单个 buffer pool 拆成 N 个（通常 N = 物理核数 / 2），每个 pool 独立 mutex、独立 LRU：

```cpp
class BufferPoolManager {
private:
    std::vector<std::unique_ptr<BufferPoolInstance>> instances_;
    size_t num_instances_;
    
public:
    Page* FetchPage(page_id_t page_id) {
        size_t idx = page_id % num_instances_;
        return instances_[idx]->FetchPage(page_id);
    }
};
```

**注意**：
- 分片函数用 `page_id % N` 即可，不用 hash（page_id 已经是均匀分布）
- 每个 instance 的 size = total_size / N
- 测试时验证：分片后命中率不应该下降（如果下降说明工作集分布不均）

**步骤 2：LRU → LRU-K 或 CLOCK（预期 +10-20%）**

纯 LRU 在 TPC-C 下会被全表扫描（Stock-Level 的范围查询）污染。改成 LRU-K（K=2）或 CLOCK：

- **LRU-K**：保留每个 page 的最近 K 次访问时间，evict 时选"距第 K 次访问最远"的 page
- **CLOCK**（更简单）：环形 buffer + access bit，扫描时跳过 access bit = 1 的页（重置为 0），淘汰 access bit = 0 的页
- **CLOCK-Pro**：在 CLOCK 基础上引入"非驻留历史"，避免反复扫描同一批冷数据

**比赛推荐**：CLOCK 或 LRU-2。CLOCK-Pro 实现复杂，收益边际递减。

**步骤 3：预读（Read-Ahead）（预期 +10-20%）**

TPC-C 的 Stock-Level 事务会扫描 ORDER-LINE 表的最近 20 个订单，这是典型的顺序访问模式。检测到顺序访问时，提前异步读取后续 page：

```cpp
// 简化的顺序检测逻辑
if (last_accessed_page_id_ == page_id - 1) {
    sequential_count_++;
    if (sequential_count_ >= 8) {
        // 异步预读后续 8 个 page
        for (int i = 1; i <= 8; i++) {
            AsyncReadPage(page_id + i);
        }
    }
} else {
    sequential_count_ = 0;
}
```

**步骤 4：Write-Behind 异步刷脏（预期 +5-10% 尾延迟改善）**

不要等到 evict 时才刷脏页，启动后台线程定期刷脏：

```cpp
// 后台线程
void BufferPoolManager::FlushDaemon() {
    while (running_) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        // 找出 dirty 且最近未访问的 page，批量刷盘
        FlushDirtyPages(/*batch_size=*/64);
    }
}
```

**好处**：evict 时不需要等 I/O，P99 latency 大幅改善。

#### 4.1.3 Buffer Pool 反模式

**❌ 反模式 1：Buffer Pool 设置过大**
- 如果 buffer pool 超过 L3 cache，每次访问都是 DRAM 延迟（80-100ns）
- 如果 buffer pool 超过物理内存，触发 swap，性能断崖式下降
- 推荐：buffer pool 占物理内存的 60-70%

**❌ 反模式 2：全局 dirty list 用一把锁**
- 刷脏线程和工作线程争用同一把锁
- 应该 per-instance 独立 dirty list

**❌ 反模式 3：page size 过大**
- TPC-C 行很小（几十到几百字节），page size 16K 可能导致一条记录修改触发整页 flush
- 推荐 page size 4K 或 8K（取决于硬件 SSD page size）

---

### 4.2 B+Tree 索引优化

#### 4.2.1 Rucbase 默认 B+Tree 的性能债

1. 全树加锁（root latch 持有整个查找过程）
2. 节点没有压缩，cacheline 利用率低
3. 分裂/合并时持有父节点写锁，阻塞并发
4. 范围扫描没有 prefetch
5. 内部节点二分查找可能用 std::lower_bound（虚函数开销）

#### 4.2.2 优化步骤

**步骤 1：Crabbing Protocol（latch coupling）（预期 +20-30%）**

实现标准的 B+Tree 并发协议：
- 搜索：从 root 开始，获取子节点 latch 后释放父节点 latch
- 插入：先乐观假设不需要分裂，只持有 leaf latch；如果真的需要分裂，再"悲观"获取从 root 到 leaf 的所有 latch

```cpp
// 乐观插入
bool BPlusTree::OptimisticInsert(const Key& key, const Value& value) {
    auto leaf = FindLeafOptimistic(key);  // 只持有 leaf 的 read latch
    if (leaf->HasSpace()) {
        leaf->UpgradeToWriteLatch();
        leaf->Insert(key, value);
        leaf->ReleaseWriteLatch();
        return true;
    }
    return false;  // 需要分裂，走悲观路径
}
```

**收益**：90% 以上的插入不需要分裂，可以走乐观路径，避免父节点锁。

**步骤 2：节点压缩与 cacheline 对齐（预期 +10-15%）**

把 B+Tree 节点大小设为 cacheline 的整数倍（通常 64 字节或 256 字节），并对齐：
- 内部节点：key 数组 + child pointer 数组，紧凑排列
- 叶子节点：key 数组 + value 数组 + next leaf pointer

**步骤 3：范围扫描 prefetch（预期 +10-20%）**

TPC-C Stock-Level 需要扫描最近 20 个 order 的所有 order-line。在 B+Tree 范围扫描时：
- 预取下一个 leaf page
- 批量返回结果（向量化）

**步骤 4：节点内部用 SIMD 查找（预期 +5-10%）**

如果 key 是 int64，节点内查找可以用 SIMD 指令并行比较 4/8/16 个 key：

```cpp
__m256i keys_vec = _mm256_loadu_si256(...);
__m256i cmp = _mm256_cmpgt_epi64(keys_vec, target);
int mask = _mm256_movemask_epi8(cmp);
int idx = __builtin_ctz(mask);
```

#### 4.2.3 B+Tree 反模式

**❌ 反模式 1：每次插入都重平衡**
- Rucbase 教学版可能实现了 B*Tree 风格的兄弟节点重平衡
- TPC-C 写入是追加为主，重平衡开销 > 直接分裂

**❌ 反模式 2：删除立即合并节点**
- TPC-C 几乎不删除，合并开销无意义
- 可以延迟合并或干脆不合并（留待 vacuum）

**❌ 反模式 3：用 std::map 实现节点内部**
- std::map 是红黑树，每个节点都 new，cache 极度不友好
- 节点内部应该用数组

---

### 4.3 锁管理器优化（TPC-C 最大瓶颈）

#### 4.3.1 为什么锁管理器是 TPC-C 的最大瓶颈

TPC-C 每个事务获取 10-30 个锁。1000 TPS 下，每秒 10000-30000 次 lock/unlock 操作。锁管理器如果不能 scale，直接卡住所有事务。

#### 4.3.2 Rucbase 默认锁管理器的问题

```cpp
class LockManager {
    std::mutex latch_;
    std::unordered_map<RID, LockRequest*> lock_table_;
    // ...
};
```

所有事务争用同一把 `latch_`，**这把锁比业务行锁本身更糟糕**——它让"并行"变成"串行"。

#### 4.3.3 优化步骤

**步骤 1：Lock Table 分片（预期 +30-50%）**

```cpp
class ShardedLockManager {
    static constexpr int kShardCount = 64;
    struct Shard {
        std::mutex latch;
        std::unordered_map<RID, LockRequest*> table;
    } __attribute__((aligned(64)));  // 避免 false sharing
    
    std::array<Shard, kShardCount> shards_;
    
    Shard& GetShard(const RID& rid) {
        size_t hash = std::hash<RID>{}(rid);
        return shards_[hash % kShardCount];
    }
};
```

**关键**：
- shard count 通常是 CPU 核数的 2-4 倍
- 每个 shard 必须 cacheline 对齐（64 字节），避免 false sharing
- 分片函数用 hash，不要用 rid % N（rid 分布不均）

**步骤 2：锁请求用对象池（预期 +5-10%）**

不要每次 lock 都 new LockRequest，用对象池：

```cpp
class LockRequestPool {
    std::vector<std::unique_ptr<LockRequest>> pool_;
    std::mutex latch_;
    
    LockRequest* Acquire() {
        std::lock_guard<std::mutex> guard(latch_);
        if (pool_.empty()) {
            return new LockRequest();
        }
        auto req = pool_.back().release();
        pool_.pop_back();
        return req;
    }
    
    void Release(LockRequest* req) {
        std::lock_guard<std::mutex> guard(latch_);
        pool_.emplace_back(req);
    }
};
```

**步骤 3：死锁检测优化**

Rucbase 默认可能是 timeout 死锁检测。优化方向：
- 用 wait-for graph 主动检测（更精准，但实现复杂）
- 用更短的 timeout（默认 1 秒，TPC-C 改成 100ms 加速死锁事务回滚）
- 用后台线程周期性检测，避免每个事务都检测

**步骤 4：意向锁优化**

TPC-C 大量使用 X 锁。检查是否可以：
- 表级 IS/IX 锁是否真的需要（如果只有单表查询，意向锁是开销）
- 行级锁是否可以"无锁升级"（用原子操作替代轻量级 X 锁）

**步骤 5：MVCC 替代读锁（如果赛题允许 Serializable 之外的隔离级别）**

MVCC 的核心思想：**读不加锁，读旧版本；写加锁，写新版本**。在 TPC-C 场景下：
- Order-Status / Stock-Level / Delivery 涉及大量读，可以从 2PL 读锁升级为 MVCC 快照读
- New-Order / Payment 的写仍走 2PL，但读 CUSTOMER/ITEM 等可以用 MVCC

**预期收益**：MVCC 实现得好，TPC-C 吞吐可以提升 50-100%。但实现成本高（需要版本链、可见性判断、vacuum），需要 3-4 周。

#### 4.3.4 锁管理器反模式

**❌ 反模式 1：锁升级（row lock → table lock）**
- TPC-C 行级冲突集中在 WAREHOUSE/DISTRICT，锁升级会让冲突更糟

**❌ 反模式 2：每次 lock 都遍历等待队列**
- 锁等待队列应该用链表，O(1) 入队出队

**❌ 反模式 3：所有锁都通过 LockManager**
- B+Tree 的 latch 应该独立于 LockManager，避免锁管理器成为瓶颈

---

### 4.4 WAL 与 Group Commit 优化

#### 4.4.1 Rucbase 默认 WAL 的问题

```cpp
void LogManager::LogRecord(const LogRecord& rec) {
    std::lock_guard<std::mutex> guard(latch_);
    buffer_.Append(rec);
    if (buffer_.size() >= kFlushThreshold) {
        fsync(fd_);
        buffer_.Clear();
    }
}
```

问题：
1. 每次 commit 都 fsync（最差情况每事务一次 fsync）
2. 全局锁串行化所有事务
3. fsync 期间所有事务阻塞

#### 4.4.2 Group Commit 实现（预期 +50-100%）

Group Commit 的核心：**多个事务的 commit 请求合并为一次 fsync**。

```cpp
class LogManager {
    std::mutex latch_;
    std::condition_variable cv_;
    std::vector<CommitRequest*> pending_commits_;
    std::thread flush_thread_;
    
    void CommitTransaction(Transaction* txn) {
        std::unique_lock<std::mutex> lock(latch_);
        CommitRequest req(txn);
        pending_commits_.push_back(&req);
        cv_.notify_one();
        req.wait(lock);  // 等待 fsync 完成
    }
    
    void FlushLoop() {
        while (running_) {
            std::unique_lock<std::mutex> lock(latch_);
            cv_.wait_for(lock, std::chrono::milliseconds(1));  // 最多等 1ms
            
            if (pending_commits_.empty()) continue;
            
            auto batch = std::move(pending_commits_);
            lock.unlock();
            
            // 把 batch 中所有事务的 log 写入 log buffer
            for (auto* req : batch) {
                log_buffer_.Append(req->txn_->log_records());
            }
            
            // 一次 fsync 持久化所有事务的 log
            fsync(fd_);
            
            // 唤醒所有等待的事务
            for (auto* req : batch) {
                req->notify();
            }
        }
    }
};
```

**关键参数**：
- `flush_interval`：1ms（推荐）— 太长会增加 commit latency，太短会让 batch 太小
- `max_batch_size`：1000（推荐）— 防止批量过大延迟过高
- 在低 TPS 时也能保证 1ms 内 commit

#### 4.4.3 双 Buffer 异步刷盘（额外 +10-15%）

```cpp
// 两个 log buffer，一个用于写，一个用于刷
char buffer_a_[LOG_BUFFER_SIZE];
char buffer_b_[LOG_BUFFER_SIZE];
char* write_buffer_ = buffer_a_;
char* flush_buffer_ = buffer_b_;

// 当 write_buffer 满或 flush timer 到达，交换 buffer
void SwapAndFlush() {
    std::swap(write_buffer_, flush_buffer_);
    // 后台线程异步 fsync flush_buffer_
    async_fsync(flush_buffer_);
}
```

**收益**：fsync 期间 write_buffer 仍可接收新 log，不阻塞事务。

#### 4.4.4 io_uring 优化（如果内核支持，额外 +10-20%）

```cpp
// 用 io_uring 提交 fsync 请求
struct io_uring ring;
io_uring_queue_init(64, &ring, 0);

struct io_uring_sqe* sqe = io_uring_get_sqe(&ring);
io_uring_prep_fsync(sqe, fd_, 0);
io_uring_submit(&ring);

// 不阻塞，继续接收新事务
```

**注意**：io_uring 在 Linux 5.1+ 才支持。比赛环境如果内核版本低，可能无法使用。

#### 4.4.5 WAL 反模式

**❌ 反模式 1：每个事务立即 fsync**
- 应该 group commit，1ms 内的 commit 合并 fsync

**❌ 反模式 2：log 文件和数据文件混在一起**
- log 应该独立磁盘，避免和数据 I/O 竞争

**❌ 反模式 3：log record 过大**
- TPC-C 一个事务的 log 应该在 100-500 字节，过大说明记录了冗余信息

---

### 4.5 查询执行优化

#### 4.5.1 Rucbase 默认执行模型的问题

Rucbase 大概率用火山模型（Volcano Iterator）：
```cpp
class Operator {
    virtual bool Next(Tuple* out) = 0;
};
```

问题：
1. 每次 Next() 都是虚函数调用
2. 一次只处理一行，cache locality 差
3. 表达式求值也是逐行

#### 4.5.2 优化步骤

**步骤 1：批量化 Next（伪向量化）（预期 +20-50%）**

不需要完整重写为向量化，只需把 Next() 改成 NextBatch()：

```cpp
class Operator {
    virtual size_t NextBatch(Tuple* out, size_t max_count) = 0;
};

// SeqScan 示例
size_t SeqScan::NextBatch(Tuple* out, size_t max_count) {
    size_t count = 0;
    while (count < max_count && HasMore()) {
        ReadNextTuple(&out[count]);
        count++;
    }
    return count;
}
```

**收益**：减少虚函数调用次数（从 N 次到 N/batch_size 次），改善 cache locality。

**步骤 2：表达式批量化求值**

不要逐行 evaluate 表达式，批量 evaluate：

```cpp
// 旧：逐行
for (auto& tuple : tuples) {
    if (EvalPredicate(tuple)) {
        output.push_back(tuple);
    }
}

// 新：批量
std::vector<bool> mask(tuples.size());
EvalPredicateBatch(tuples, &mask);
for (size_t i = 0; i < tuples.size(); i++) {
    if (mask[i]) output.push_back(tuples[i]);
}
```

**步骤 3：Hash Join 实现（预期对 Order-Status 等 +30-50%）**

Rucbase 默认可能是 NestedLoopJoin。对 TPC-C 的 Order-Status（按 CUSTOMER 反查 ORDER）等场景，Hash Join 远快于 NestedLoopJoin：

```cpp
class HashJoin : public Operator {
    void Build() {
        while (left_->NextBatch(batch, kBatchSize)) {
            for (auto& t : batch) {
                hash_table_[Hash(t)].push_back(t);
            }
        }
    }
    
    size_t NextBatch(Tuple* out, size_t max_count) {
        // Probe 阶段
    }
};
```

**步骤 4：Hash Aggregation**

TPC-C Stock-Level 需要聚合 ORDER-LINE 的数量。用 hash aggregation 而非 sort aggregation：

```cpp
class HashAgg : public Operator {
    std::unordered_map<Key, AggState> hash_table_;
    
    size_t NextBatch(Tuple* out, size_t max_count) {
        while (input_->NextBatch(batch, kBatchSize)) {
            for (auto& t : batch) {
                hash_table_[GetKey(t)].Update(t);
            }
        }
        // 返回聚合结果
    }
};
```

#### 4.5.3 查询执行反模式

**❌ 反模式 1：所有 join 都用 NestedLoopJoin**
- TPC-C 的 Order-Status 用 NLJ 会很慢

**❌ 反模式 2：每次 Next() 都重新打开算子**
- Init/Next 应该分离，Init 只做一次

**❌ 反模式 3：表达式不编译**
- 同一个表达式反复 evaluate，应该预编译为 bytecode 或直接 LLVM IR

---

### 4.6 事务与 MVCC（如果选择实现）

#### 4.6.1 MVCC 的取舍

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|-------|
| 纯 2PL | 实现简单，赛题默认 | TPC-C 锁竞争激烈，吞吐低 | 仅 baseline |
| MVCC + 2PL（混合） | 读不阻塞写，写不阻塞读 | 实现复杂，需要 vacuum | ★★★★★ |
| 纯 OCC | 乐观，无锁 | 高冲突下 abort 多 | ★★ |
| 纯 MVCC（SSI） | 完全 Serializable | 实现极复杂 | ★ |

**比赛推荐**：MVCC + 2PL 混合，类似 PostgreSQL 的设计：
- 读：MVCC 快照读，不加锁
- 写：2PL 行级锁
- 隔离级别：Read Committed（不需要 Serializable，赛题通常接受 RC）

#### 4.6.2 MVCC 实现要点

```cpp
struct Tuple {
    RID rid;
    TxnID xmin;  // 创建该版本的事务 ID
    TxnID xmax;  // 删除该版本的事务 ID
    TupleData data;
    Tuple* next_version;  // 版本链
};

bool MVCC::IsVisible(Tuple* tuple, Snapshot snapshot) {
    // 1. xmin committed 且 < snapshot
    // 2. xmax 不存在 或 未 committed 或 > snapshot
    return IsCommittedBefore(tuple->xmin, snapshot) &&
           (tuple->xmax == INVALID_TXN || 
            !IsCommittedBefore(tuple->xmax, snapshot));
}
```

#### 4.6.3 MVCC 反模式

**❌ 反模式 1：版本链无界增长**
- 必须有 vacuum 清理旧版本，否则 buffer pool 被填满

**❌ 反模式 2：每次读都遍历版本链**
- 版本链应该用 inline 优化（最新版本在 tuple slot，旧版本在 undo log）

**❌ 反模式 3：snapshot 用物理时钟**
- 物理时钟在多核下需要全局同步，用 monotonic transaction ID 更好

---

## 第五部分：决赛冲刺策略

### 5.1 决赛前 2 周——锁定收益，停止冒险

**禁忌**：
- 不要在决赛前 1 周做大改动（MVCC、向量化这种 3+ 周工作量）
- 不要重写整个模块
- 不要尝试新技术（io_uring、eBPF）
- 不要调参赛框架版本（升级编译器、依赖库）

**该做**：
- 每天跑 TPC-C benchmark，记录 tpmC
- perf top 持续观察，找剩余的 1-2 个低垂果实
- 微调参数（buffer pool size、log flush interval、batch size）
- 准备答辩材料（baseline 数据、优化路线图、火焰图对比）

### 5.2 决赛环境适配

**T + 7 天**：搞清楚决赛的硬件配置
- CPU 型号、核数、NUMA 拓扑
- 内存大小、内存频率
- 磁盘类型（NVMe SSD / SATA SSD / HDD）
- 内核版本（决定是否能用 io_uring）
- 文件系统（ext4 / xfs）

**T + 5 天**：根据硬件调优
- buffer pool size = 物理内存 × 0.6
- 如果是 NUMA，启用 numactl --interleave=all
- 如果是 NVMe，I/O queue depth 调到 64+
- 如果内核 ≥ 5.1，启用 io_uring

### 5.3 答辩高分技巧

答辩评委会同时看**性能数字**和**故事性**。准备 3-5 个"亮点优化"：

1. **故事化的优化路径**：
   - "我们发现 baseline 的 tpmC 是 X，火焰图显示锁管理器占 40% CPU"
   - "通过将锁表分片为 64 个 shard，tpmC 提升到 1.5X"
   - "进一步分析发现 WAL fsync 是新瓶颈，实现 group commit 后达到 2X"
   - "最后通过 MVCC 把读锁开销消除，达到 3X"

2. **可视化**：
   - baseline → 各阶段 tpmC 增长柱状图
   - before/after 火焰图对比
   - P50/P99 latency 下降曲线
   - 架构演进图

3. **创新点提炼**：
   - 不要说"我们做了 group commit"（人人都做）
   - 要说"我们设计了自适应 batch size 的 group commit，低负载时 1ms flush，高负载时 batch 满 flush"（具体且新颖）
   - 不要说"我们做了 buffer pool 分片"（人人都做）
   - 要说"我们用 page_id 亲和性分片，保证同一表的 page 落在同一 shard，避免跨 shard 同步"（具体）

4. **避坑提醒**：
   - 不要强调"我们做了分布式"（TPC-C 单机，无关）
   - 不要强调"我们实现了完整 SQL"（TPC-C 只用 5 类固定 SQL）
   - 不要强调"我们支持多种索引"（B+Tree 够用）
   - 评委关注的是**性能数字背后的方法论**，不是功能完整性

---

## 第六部分：反模式与踩坑清单（决赛前必读）

### 6.1 比赛级反模式

**❌ 反模式 1：过早优化**
- 在功能题还没完全通过时就开始性能优化
- 后期修 bug 时优化代码反而增加复杂度

**❌ 反模式 2：过度工程化**
- 给简单模块加各种抽象层（接口、模板、继承）
- TPC-C 不需要"扩展性"，需要"性能"

**❌ 反模式 3：盲目相信论文数字**
- 论文里 "10x speedup" 是在特定场景下
- TPC-C 场景可能完全不适用的论文方法

**❌ 反模式 4：忽视正确性**
- 优化后跑过 TPC-C 正确性测试吗？
- 有些优化（如 MVCC）可能引入难以察觉的一致性 bug
- 决赛如果正确性测试不通过，性能再高也是 0 分

**❌ 反模式 5：抄冠军代码**
- 2024/2025 冠军代码都开源了，但**直接抄会被取消资格**
- 可以借鉴思路（"他们做了 group commit"，"他们用了 MVCC"）
- 实现必须自己写

**❌ 反模式 6：忽视 P99 latency**
- 有些优化提升平均吞吐但恶化 P99
- 评委可能同时看 P99，要平衡

**❌ 反模式 7：没有 baseline 数据**
- 没有初始 baseline 就开始优化，无法证明"提升"
- 答辩时被问"baseline 是多少"会答不上

**❌ 反模式 8：未做长期稳定性测试**
- 有些优化短期快，长期慢（如内存碎片化）
- 至少跑 1 小时 TPC-C 验证

### 6.2 Rucbase 特定踩坑

**踩坑 1：B+Tree 实现可能有线程安全 bug**
- 教学版 B+Tree 的并发控制可能不完整
- 高并发下偶发崩溃，需要先做 stress test

**踩坑 2：DiskManager 的 fd 数量限制**
- 如果每个文件一个 fd，表多时 fd 用尽
- 用单一大文件 + offset 替代多文件

**踩坑 3：lock manager 的死锁检测可能漏检**
- timeout 检测可能误判（事务确实慢但未死锁）
- wait-for graph 可能漏边

**踩坑 4：log manager 的 fsync 可能不可靠**
- 某些文件系统 fsync 不保证持久化（如 ext3 的 data=writeback）
- 用 O_DIRECT + fsync 双保险

**踩坑 5：buffer pool 的 page 替换可能引发 thrashing**
- 工作集略大于 buffer pool 时会反复换入换出
- 测试不同 buffer pool size 找拐点

### 6.3 答辩级踩坑

**踩坑 1：性能数字"超出物理极限"**
- 如果报告 tpmC 超过理论 CPU 上限，评委会质疑
- 提前计算理论上限（CPU 频率 × 核数 / 单事务 CPU cycle）

**踩坑 2：火焰图显示异常**
- 优化后火焰图显示"几乎不消耗 CPU"，但 tpmC 不高 → 可能是 I/O bound 或锁等待
- 用 off-CPU 火焰图补充

**踩坑 3：对评委提问准备不足**
- "你们为什么不用 MVCC 而用 2PL？"（如果用 2PL）
- "你们的 group commit batch size 怎么定的？"
- "buffer pool 大小为什么是这个值？"
- "如果给你们更长时间，下一个优化方向是什么？"

---

## 第七部分：参考资源与学习路径

### 7.1 必读论文与文档

1. **Hellerstein, Stonebraker, Hamilton — *Architecture of a Database System* (2007)**
   - 数据库架构全景，理解各模块关系

2. **CMU 15-445/645 Database Systems (Andy Pavlo)**
   - 课程视频 + Lab（Buffer Pool、B+Tree、Query Execution、Concurrency Control）
   - https://15445.courses.cs.cmu.edu/

3. **CMU 15-721 Advanced Database Systems**
   - 进阶性能优化专题
   - https://15721.courses.cs.cmu.edu/

4. **Thomas Neumann — *Efficiently Compiling Efficient Query Plans for Modern Hardware* (VLDB 2011)**
   - 查询执行 codegen 经典论文

5. **Mohur Biswas et al. — *Closing the B+-tree vs. LSM-tree Write Amplification Gap* (FAST 2022)**
   - B+Tree 写放大优化

### 7.2 必看开源代码

1. **Rucbase 官方仓库**：https://github.com/ruc-deke/rucbase-lab
   - 仔细读每个 Lab 的实验文档

2. **CMU BusTub**：https://github.com/cmu-db/bustub
   - Rucbase 的灵感来源，架构相似
   - 重点关注 buffer_pool_manager、b_plus_tree、lock_manager

3. **PostgreSQL 源码**：https://github.com/postgres/postgres
   - 不要全读，按需查找特定模块
   - 重点：src/backend/storage/buffer/、src/backend/storage/lmgr/、src/backend/access/transam/

4. **2024 冠军代码（借鉴思路，禁止抄袭）**：https://github.com/Kosthi/CSCC-DB-Rucbase-2024
   - 看他们的 README、commit history、docs
   - 学习他们的优化路线，不抄代码

5. **2025 冠军代码**：https://github.com/RushDB-Lab/CSCC-DB-Rucbase-2025
   - 同上，借鉴思路

### 7.3 工具与命令

```bash
# 火焰图
perf record -F 99 -p <pid> -g -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# off-CPU 火焰图（看锁等待）
perf record -F 99 -p <pid> -g -e sched:sched_switch -- sleep 30

# syscall 直方图
perf stat -e 'syscalls:sys_enter_*' -p <pid> -- sleep 30

# 内存分配追踪
perf record -e kmem:mm_page_alloc -p <pid> -- sleep 30

# I/O 延迟分布
iostat -x 1

# 锁竞争分析
perf lock record -p <pid> -- sleep 30
perf lock report

# bpftrace 一行命令
bpftrace -e 'tracepoint:syscalls:sys_enter_futex { @[comm] = count(); }' -p <pid>

# TPC-C 测试（参考 Kosthi 仓库的脚本）
# https://github.com/Kosthi/CSCC-DB-Rucbase-2024
```

### 7.4 学习路径建议（3-6 个月）

**第 1 个月：打基础**
- 完整阅读 Rucbase 源码（每个模块）
- 完成 CMU 15-445 Lab 1-4（Buffer Pool / B+Tree / Query / Concurrency）
- 跑通 TPC-C，建立 baseline

**第 2 个月：P0 优化**
- WAL Group Commit
- Lock Manager 分片
- Buffer Pool 分片

**第 3 个月：P1 优化**
- B+Tree 乐观锁
- MVCC 实现（如果时间允许）
- 算子批量化

**第 4 个月：P2 优化**
- CBO 优化器（精简版）
- Hash Join
- io_uring（如果内核支持）

**第 5 个月：调优 + 答辩准备**
- 微调参数
- 性能数据可视化
- 答辩 PPT

**第 6 个月（决赛前）：**
- 冻结代码，不再大改
- 每天跑 benchmark
- 模拟答辩

---

## 第八部分：元反思 — 给你的最后建议

### 8.1 比赛是工程问题，不是科研问题

不要陷入"找一个理论上更好的算法"的陷阱。比赛的本质是：**用现有技术，做出比 baseline 快 5-10 倍的实现**。

- 不要重新发明数据结构（用 B+Tree，不要发明新树）
- 不要追求"原创性"（学习 PostgreSQL 的实现是合理的）
- 不要陷入"完美主义"（能跑、能 scale、能通过正确性测试就行）

### 8.2 测量是优化的灵魂

**没有 perf 数据的优化都是猜测。**每天至少跑一次 perf + flamegraph，每次优化前后必须对比数据。建立性能 dashboard：
- baseline tpmC
- 各阶段 tpmC
- P50/P99 latency
- CPU utilization
- IOPS
- buffer pool hit rate
- lock wait time

### 8.3 团队协作的关键

如果团队 ≥ 3 人，必须分工明确：
- 1 人负责 buffer pool + B+Tree（存储层）
- 1 人负责 lock manager + WAL + 事务（并发与持久化）
- 1 人负责 query execution + optimizer（查询层）
- 每周对齐接口，避免合并冲突

**禁忌**：3 人都改同一模块，会互相覆盖。

### 8.4 心态管理

比赛周期长（3-6 个月），中间会经历多次"为什么这么慢"的挫败时刻。建议：
- 每周一次 retrospective，记录本周进展（哪怕是负向的）
- 不和别的队比较 tpmC，只和自己的 baseline 比
- 决赛前 1 个月开始准备答辩，不要等代码完成才开始

### 8.5 写在最后

Rucbase 比赛的真正价值不是"得了一等奖"，而是在 3-6 个月内**深度经历一次数据库内核从读代码到改代码到优代码的完整过程**。这个过程会让你在面试、研究生申请、工作实习中受益终生。

性能优化的本质是"理解系统"。当你能把 Rucbase 的每一行代码、每一个锁、每一次 I/O 都讲清楚时，你已经是数据库内核工程师了。一等奖只是这个过程的副产品。

祝比赛顺利。
