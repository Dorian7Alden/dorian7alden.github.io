# buffer_pool_manager 特性

## 并发模型

- **值/范围**：全局 `std::mutex latch_`，所有公开 API（fetch_page / new_page / unpin_page / flush_page / delete_page / flush_all_pages / delete_all_pages）加同一把锁
- **性质**：静态推导
- **来源**：`buffer_pool_manager.cpp:33,70,105,134,161,197,221`
- **优化关联**：同一时刻只有一个线程在执行任何 BPM 操作。磁盘 I/O（read_page、脏页 write_page）在持锁期间执行，其他线程的热路径命中也被阻塞

## 锁的调用约定

- **值/范围**：顶层 API 加锁，内部辅助函数（find_victim_page / update_page / flush_log_before_page_write）不加锁，调用方已持锁
- **性质**：静态推导
- **来源**：`buffer_pool_manager.cpp:14-18` 注释块，`.h:86-89` private 声明
- **优化关联**：调用 Replacer 的方法时已持有 latch_，Replacer 内部的锁是冗余的

## page_table_ 查找

- **值/范围**：`unordered_map<PageId, frame_id_t, PageIdHash>`，哈希函数为 `(fd << 16) | page_no`。池满时最多 65536 条目
- **性质**：静态推导
- **来源**：`buffer_pool_manager.h:33`
- **优化关联**：fd 通常 3~100，page_no 递增，低位完全由 page_no 决定，分布不均匀。详见 `dev-doc/performance-improve/02-pageid-hash-optimization.md`

## 帧生命周期

- **值/范围**：初始化全部在 free_list_ → fetch_page/new_page 从 free_list_ 或 replacer 获取 → unpin_page pin_count=0 时进入 replacer → 被 victim 选中后淘汰。page_table_ 始终反映当前帧→PageId 映射
- **性质**：静态推导
- **来源**：`buffer_pool_manager.cpp` 各 API 的组合行为
- **优化关联**：free_list_ 用 `std::list<frame_id_t>`，但只在构造时批量插入和在两端操作（front/push_back），用 deque 或简单数组+游标更省分配

## fetch_page miss 路径上的操作序列

- **值/范围**：持锁期间依次执行：hash 查找 → find_victim_page（查 free_list_ 或 replacer->victim）→ update_page（可能脏页刷盘）→ disk read（16KB I/O）→ replacer->pin → pin_count=1
- **性质**：静态推导
- **来源**：`buffer_pool_manager.cpp:31-60`
- **优化关联**：(1) update_page 内的脏页刷盘和后续 read_page 是 I/O 操作，在持锁期间阻塞所有线程；(2) update_page 的 reset_memory（memset 16KB）在 read_page 之前执行，read_page 紧接着全量覆盖，memset 是浪费

## pool_size_ 实际值

- **值/范围**：由 `BUFFER_POOL_SIZE` 配置决定，默认 65536。每个 Page 16KB（PAGE_SIZE），总内存约 1GB
- **性质**：静态推导
- **来源**：`buffer_pool_manager.h:31`，`config.h`
- **优化关联**：pages_ 数组一次性 new 分配，连续内存，cache 友好。但 1GB 池在 16 实例分片时每实例 64MB，足够

## Replacer 选择逻辑

- **值/范围**：构造函数中三个分支全部创建 `LRUReplacer`，`std::string::compare` 语义反了（相等返回 0 为 false，所以 "LRU" 走 else 分支，"CLOCK" 和空串走 if 分支——但最终都是 LRUReplacer）
- **性质**：静态推导（死代码）
- **来源**：`buffer_pool_manager.h:48-53`
- **优化关联**：不影响运行，但代码意图混乱。如果要支持多种 Replacer，需修正 compare 逻辑
