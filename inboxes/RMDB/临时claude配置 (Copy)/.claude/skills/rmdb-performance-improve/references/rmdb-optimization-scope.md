# RMDB 专项优化参考

从《数据库设计大赛-TPC-C性能优化实战方法论》和《数据库内核性能优化方法论》中提炼的，与 RMDB 直接相关的优化知识。

## 一、RMDB 模块级性能债

教学框架为可读性做的性能牺牲，按模块归类：

### storage/ — 存储层

| 问题 | 表现 | 优化方向 |
|------|------|----------|
| DiskManager 同步 I/O | 每次 read/write 一次 syscall | pread/pwrite 合并 lseek+read/write |
| Page 格式冗余 | 页头过大、slot 目录低效 | 紧凑化页布局 |
| 单 fd 管理 | 多表时可能 fd 不够 | 检查 fd 复用策略 |

### buffer_pool_manager / replacer — 缓存层

| 问题 | 表现 | 优化方向 |
|------|------|----------|
| 单实例单 mutex | 所有线程争用同一把锁 | 按 page_id % N 分片，N=核数/2 |
| 纯 LRU | 全表扫描污染热数据 | midpoint insertion（old/young 分区）|
| Evict 时刷脏 | 尾部延迟尖刺 | 后台 write-behind 主动刷脏 |
| 无预读 | 顺序访问未优化 | 检测连续访问模式，预读后续 page |

### index/ — B+Tree 索引

| 问题 | 表现 | 优化方向 |
|------|------|----------|
| 全树加锁 | 遍历期间持有 root latch | crabbing protocol（latch coupling） |
| 悲观插入 | 插入总是从 root 到 leaf 全加锁 | 乐观插入：先假设不需要分裂 |
| 节点用 STL 容器 | std::map/vector 非 cache 友好 | 用连续数组，cacheline 对齐 |
| 无范围扫描 prefetch | 逐页加载 | 预取下一个 leaf page |

### concurrency/ — 锁管理器

| 问题 | 表现 | 优化方向 |
|------|------|----------|
| 全局 lock table mutex | 所有 lock/unlock 串行化 | 按 RID hash 分片（shard count=核数×2-4）|
| 每次 new LockRequest | malloc 开销在热路径 | 对象池复用 |
| Timeout 死锁检测 | 等待固定时间才回滚 | wait-for graph 主动检测，或短 timeout（100ms） |

### recovery/ — WAL 日志

| 问题 | 表现 | 优化方向 |
|------|------|----------|
| 每次 commit 独立 fsync | 每事务一次 fsync（~1ms） | group commit：攒批 1ms 内事务合并 fsync |
| 全局 log mutex | 所有线程串行写 log | lock-free：per-thread buffer + atomic link |
| fsync 阻塞写入 | flush 期间新事务被阻塞 | 双 buffer 异步刷盘 |

### execution/ — 查询执行

| 问题 | 表现 | 优化方向 |
|------|------|----------|
| 火山模型逐行 next() | 每行一次虚函数调用 | 批量化 NextBatch(batch, max_count) |
| 无 plan cache | 同一条 SQL 反复 parse | 缓存 prepared statement |
| 可能只有 NLJ | Order-Status 等反查慢 | 实现 Hash Join |

## 二、优化优先级

按投入回报比（ROI）排序，适合在有限时间内最大化收益：

### P0 — 高 ROI，低工程投入（1-2 周）

1. **WAL Group Commit**：预期 +50-100% 吞吐。攒批 1ms 内事务，合并为一次 fsync
2. **锁管理器分片**：预期 +30-50%。按 RID hash 分片 lock table，每 shard 独立 mutex
3. **Buffer Pool 分片**：预期 +20-30%。按 page_id % N 拆成多实例
4. **pread/pwrite 替代 lseek+read/write**：预期 +5-15%。减少一半 syscall

### P1 — 中 ROI，中等工程投入（2-4 周）

5. **B+Tree 乐观锁（latch coupling）**：预期 +20-40%。搜索时逐级释放父节点 latch
6. **Buffer Pool midpoint insertion**：预期 +10-20%。old/young 分区防止扫描污染
7. **算子批量化**：预期 +20-50%。Next() → NextBatch()，减少虚函数调用
8. **Buffer Pool 预读**：预期 +10-20%。检测顺序访问，异步预取

### P2 — 低 ROI 或高工程投入（3+ 周）

9. **内存池替代 new/delete**：预期 +10%
10. **Hash Join 实现**：预期 +10-20%
11. **Plan cache**：预期 +5-10%
12. **MVCC 替代 2PL 读锁**：预期 +50-100%，但工程投入 3-4 周

## 三、不该先做的事

- 不要先实现完整 CBO 优化器（TPC-C 查询模式简单，RBO 已够用）
- 不要先实现向量化执行引擎（除非 P0/P1 全部完成）
- 不要先实现 LLVM JIT codegen（投入极大，TPC-C 收益有限）
- 不要先重写存储引擎（B+Tree → LSM）（TPC-C 读多写少，B+Tree 更合适）
- 不要盲目调大 buffer pool 而不分析命中率（如果命中率已 99%，调大无收益）
- 不要增加线程数而不消除锁竞争（线程数越多锁竞争越激烈）

## 四、常见陷阱

### 指标误读

- **Buffer pool hit rate 99% ≠ 性能好**：全表扫描预读让 hit rate 虚高。用 `pages_read/sec` 替代
- **CPU 100% ≠ 瓶颈**：可能是健康的（在做有用功）。判断 `%sys` 占比——高 `%sys` 可能在 context switch 或 page fault
- **IOPS 高 ≠ 磁盘瓶颈**：NVMe 单盘 IOPS 可达 100 万+。看 `await` 而非 IOPS

### 优化误区

- **过早优化**：功能题没通过就不要开始性能优化
- **过度工程化**：给简单模块加抽象层。TPC-C 需要"性能"而非"扩展性"
- **盲目信论文数字**：论文里的"10× speedup"在特定场景下。TPC-C 场景可能完全不同
- **忽视正确性**：优化后必须通过正确性测试。MVCC 等优化可能引入隐蔽一致性 bug

### perf 使用陷阱

- 30 秒的 `perf record` 可能恰好覆盖一次 checkpoint flush，误判瓶颈
- 采样型工具（99Hz perf）对 1ms 级别的尖峰不敏感——短查询有 90% 概率不被采样
- 聚合指标掩盖尾部分布——avg latency 5ms 可能 p99=200ms
