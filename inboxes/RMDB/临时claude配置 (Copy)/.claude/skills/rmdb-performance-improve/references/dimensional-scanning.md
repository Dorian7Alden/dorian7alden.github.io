# 方法论三：维度扫描

适合：没有明确测量数据，需要系统性地启发优化灵感的场景。

核心思想：不凭空思考，而是按照预定义的维度清单逐一排查每个层面可能的优化方向。维度参考《数据库内核性能优化方法论》的 12+1 维度框架，按 RMDB 当前发展阶段裁剪为 8 个可操作维度。

## 八个扫描维度

### 维度 1：存储引擎 — 数据布局与 I/O

- **页设计**：Page 大小是否匹配硬件（SSD page 16KB，文件系统 block 4KB）？页内记录密度是否最大化？空闲空间管理是否高效？
- **数据布局**：行存格式——定长/变长字段的偏移计算、NULL bitmap 开销、行头大小。是否存在填充浪费？
- **I/O 模式**：每次读写是否合并了相邻操作？是否有冗余的 lseek+read/write（应改用 pread/pwrite）？写放大如何——一次逻辑写触发了几次物理 I/O？
- **文件管理**：DiskManager 的文件描述符管理——多表时 fd 是否够用？是否可以用单一大文件 + offset 替代多文件？

对应 RMDB 模块：`storage/disk_manager`、`storage/page`、`record/`

> 参考：FAST22 论文用 SSD 内置压缩把 B+Tree 写放大从 50× 降到 5×，揭示了"硬件抽象层重新定义数据结构权衡"的范式。

### 维度 2：Buffer Pool — 缓存与淘汰

- **替换算法**：当前是纯 LRU 还是变种？全表扫描是否会污染热数据（需要 midpoint insertion / LRU-K / CLOCK）？
- **并发控制**：buffer pool 是否单实例单 mutex？是否可按 page_id 分片（多 instance，每 instance 独立 mutex）？
- **预读策略**：是否检测顺序访问模式并预读后续 page？linear read-ahead 和 random read-ahead 的触发条件是否合理？
- **刷脏策略**：dirty page 在 evict 时才写盘还是后台 write-behind 主动刷？前者会导致尾部延迟尖刺。
- **Page 访问开销**：FetchPage 路径上的锁持有时间是否可缩短？page 的 pin/unpin 是否有冗余操作？

对应 RMDB 模块：`storage/buffer_pool_manager`、`replacer/`

> 常见误判：buffer pool hit rate 99% 不代表性能好——全表扫描的预读会让 hit rate 虚高，且 hit rate 对突发抖动不敏感。用 `pages_read/sec` 和 `pages_written/sec` 替代 hit rate 判断真实 I/O 压力。

### 维度 3：索引结构 — B+Tree

- **并发协议**：当前是 crabbing protocol（latch coupling）还是全树加锁？是否实现了乐观插入（先假设不需要分裂，只持 leaf latch）？
- **节点组织**：内部节点和叶子节点的 key/value 排列是否 cacheline 友好？是否用数组而非链表/红黑树？
- **分裂/合并**：插入触发分裂时持有父节点写锁的范围和时长？TPC-C 几乎不删除，合并逻辑是否可以简化？
- **范围扫描**：是否有 leaf page 间的 next pointer 实现高效遍历？是否有 prefetch？
- **Key 编码**：复合 key 的编码比较是否高效？是否有冗余的序列化/反序列化？

对应 RMDB 模块：`index/`、`ix_index_handle`

> 关键优化：90% 以上的插入不需要分裂，可以走乐观路径（只持 leaf latch）。只有在确实需要分裂时才退化为悲观路径（从 root 到 leaf 全加锁）。

### 维度 4：查询处理 — 执行模型与算子

- **执行模型**：火山模型（逐行 next）→ 向量化（逐批 next）。批量化可以减少虚函数调用开销（从 N 次降到 N/batch_size 次），改善 cache locality。
- **算子效率**：JOIN 算法——NestedLoopJoin vs HashJoin。TPC-C 的 Order-Status 按 CUSTOMER 反查 ORDER，Hash Join 远快于 NLJ。聚合——SortAgg vs HashAgg。
- **表达式求值**：是否有 plan cache 避免重复 parse + optimize？表达式是否预编译为 bytecode 而非逐行解释？
- **快速路径**：`SELECT COUNT(*)`、主键点查等常见模式是否可短路，不走完整执行路径？

对应 RMDB 模块：`parser/`、`analyze/`、`planner/`、`execution/`

> 向量化的最佳点在"中等到大数据量"区间。OLTP 点查（返回 1 行）走向量化反而是负担——batch 打包/拆包开销在 1 行结果上是纯浪费。CockroachDB 的设计是 OLTP 点查走行式、OLAP 走向量化。

### 维度 5：并发与事务 — 锁与闩锁

- **锁管理器**：lock table 是否单实例单 mutex？是否可按 RID hash 分片？每个 shard 是否 cacheline 对齐避免 false sharing？
- **锁请求分配**：每次 lock/unlock 是否都 new/delete LockRequest？是否可用对象池复用？
- **死锁检测**：timeout 检测还是 wait-for graph？检测频率和开销如何？
- **闩锁（Latch）**：保护内存结构（buffer pool page、B+Tree 节点）的闩锁是否做了读写分离？持有时间是否可缩短？
- **隔离级别**：当前是 2PL 还是 MVCC？读操作是否可以不阻塞写操作？

对应 RMDB 模块：`concurrency/`、`transaction/`

> TPC-C 每个事务获取 10-30 个锁。1000 TPS 下每秒 10000-30000 次 lock/unlock。锁管理器如果不能 scale，直接卡住所有事务。这是 TPC-C 最大的瓶颈。

### 维度 6：WAL 与持久化 — 日志与恢复

- **刷盘频率**：每次 commit 都 fsync？还是 group commit 合并多个事务的 fsync？
- **日志写入并发**：log buffer 写入是否用全局锁串行化？是否可改为 lock-free（per-thread buffer + atomic link）？
- **日志格式**：每条 log record 的大小是否紧凑？是否有冗余字段？二进制编码 vs 文本格式？
- **双缓冲**：fsync 期间 write_buffer 是否仍可接收新 log（双 buffer 交换）？
- **I/O 接口**：同步 fsync 还是 io_uring 异步提交？fdatasync 是否可替代 fsync（省 metadata 刷盘）？

对应 RMDB 模块：`recovery/`

> Group commit 的核心：多个事务的 commit 请求合并为一次 fsync。flush interval 推荐 1ms——太长增加 commit latency，太短让 batch 太小。

### 维度 7：内存与数据流 — 分配与拷贝

- **内存分配**：malloc/free 频率是否过高？是否可用内存池/Arena 减少分配开销？
- **数据拷贝**：路径上是否有不必要的复制？内存缓冲区到 Page 对象的数据搬运是否可以消除？
- **数据结构紧凑度**：是否用指针链表（cache 不友好）而非连续数组？struct 字段排列是否考虑了 cacheline 对齐？
- **冷热分离**：高频访问字段和低频访问字段是否在同一 cacheline（导致 false sharing）？

对应 RMDB 模块：全局

> jemalloc 相比 glibc ptmalloc2 在长跑数据库上碎片率更低、多 arena 并发更好。但换分配器不是银弹——对超大对象（>16MB）jemalloc 会退化为 mmap。

### 维度 8：观测与测量 — 性能可视化

- **热点分析**：是否定期跑 `perf record` + 火焰图？on-CPU 火焰图（CPU 在哪里烧）和 off-CPU 火焰图（线程在等什么）是否都覆盖？
- **syscall 统计**：`perf stat` 或 `strace -c` 看哪些 syscall 调用最多。futex 高 → 锁竞争；fsync 高 → WAL 串行化；read 高 → buffer pool miss。
- **延迟分布**：是否记录了 P50/P99/P999 而非只看平均值？avg latency 5ms 可能意味着 p50=2ms + p99=200ms。
- **资源 USE 检查**：CPU/内存/磁盘/网络的 Utilization、Saturation、Errors 是否逐一排查？

> 观测者效应：`perf record -F 99` 整体开销约 1-3%，可以长期运行。`strace -p` 开销可高达 10×，生产环境禁用。判断观测开销是否可接受：对 p99 latency 的影响是否小于 5%。

## 使用方式

每次探索时，不一定要扫描全部八个维度。选一个最相关的维度深入排查，找出 2-3 个优化灵感后再决定是否继续扫描其他维度。

如果已经有测量数据，优先用假设驱动法（`hypothesis-driven.md`）在该维度内做精准验证。
