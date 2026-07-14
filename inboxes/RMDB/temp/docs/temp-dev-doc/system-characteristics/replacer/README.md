# replacer 特性

## LRU 数据结构

- **值/范围**：`std::list<frame_id_t>` LRUlist_（队列）+ `std::unordered_map<frame_id_t, iterator>` LRUhash_（O(1) 定位）。队首最近使用，队尾最久未使用
- **性质**：静态推导
- **来源**：`lru_replacer.h:42-43`
- **优化关联**：list::emplace_front（unpin 路径）每次分配一个链表节点（堆 malloc）；list::erase（pin 路径）释放节点

## 内部锁冗余

- **值/范围**：victim / pin / unpin 三个方法各自 `std::scoped_lock{latch_}`。但调用方 BufferPoolManager 在所有公开 API 入口已持有全局 latch_，没有其他调用方能并发访问 Replacer
- **性质**：静态推导
- **来源**：`lru_replacer.cpp:24,42,58` vs `buffer_pool_manager.cpp:33`
- **优化关联**：每次 replacer 调用执行一次冗余的 mutex lock+unlock。fetch_page 命中路径经历 BPM latch_ + Replacer latch_ 两层锁。去掉内层锁无正确性风险，每次调用省一对 lock/unlock

## unpin 的内存分配

- **值/范围**：每次 `unpin` → `LRUlist_.emplace_front(frame_id)` → 一次堆分配（std::list 节点 ≈ 24 字节 + 开销）+ `LRUhash_.try_emplace(frame_id, iterator)` → 一次哈希表插入（可能触发 rehash）
- **性质**：静态推导
- **来源**：`lru_replacer.cpp:68-70`
- **优化关联**：高 TPS 下 unpin 频次可达每秒数万次，对应每秒数万次 malloc。预分配节点池或改用 std::deque（不释放节点内存）可减少分配压力

## victim 的 O(1) 特性

- **值/范围**：victim 从队尾取 frame_id（back + pop_back + hash erase），三个操作均为 O(1)。选出的帧号交给 BPM 执行实际的淘汰动作（刷脏、清零、切换身份）
- **性质**：静态推导
- **来源**：`lru_replacer.cpp:29-32`
- **优化关联**：victim 本身已最优。瓶颈不在 Replacer 的选择逻辑，而在 BPM 拿到 frame_id 后的 I/O 操作

## max_size_ 边界

- **值/范围**：等于 pool_size_（缓冲池帧数，默认 65536）。unpin 时若 list 已满则静默丢弃（防御性编程），实际上不可达——每个帧要么在 free_list_ 要么在 replacer，总数不会超过 pool_size_
- **性质**：静态推导
- **来源**：`lru_replacer.cpp:61`
- **优化关联**：这个检查是防御性的，正常路径上的开销可忽略

## 纯 LRU 无 midpoint insertion

- **值/范围**：所有 unpin 的帧插入队首，所有 victim 从队尾取。全表扫描的页面和新到的热页在 LRU 链中无差别对待
- **性质**：静态推导
- **来源**：`lru_replacer.cpp:68` emplace_front，`:30` back+pop_back
- **优化关联**：全表扫描可能把真正的热页推入队尾并淘汰，导致后续访问 miss。LRU-K 或 midpoint insertion（如 PostgreSQL 的 5/8 分割点）可缓解，但复杂度显著增加
