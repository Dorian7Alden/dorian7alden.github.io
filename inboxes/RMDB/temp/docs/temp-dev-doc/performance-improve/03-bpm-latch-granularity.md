# 03 BufferPoolManager 锁粒度优化预案

**状态**：识别阶段，待实测验证。

## 当前状况

`BufferPoolManager` 所有公开方法（`fetch_page`、`new_page`、`unpin_page`、`flush_page`、`delete_page`、`flush_all_pages`）都使用全局 `std::mutex latch_` 保护。一把锁串行化所有并发访问。

`fetch_page` 的典型执行路径：

```
scoped_lock(latch_)              ← 全局锁
  page_table_.find()
  replacer_->pin()
  find_victim_page()             ← 访问 free_list_ + replacer_
  update_page()                  ← 可能刷脏页（含 WAL flush + write_page）
  disk_manager_->read_page()     ← 纯磁盘 I/O，占锁期间的大头
  replacer_->pin() + pin_count_++
scoped_lock 析构                 ← 解锁
```

## 问题分析

两处持锁期间的操作与锁保护的共享数据无关：

1. **`update_page` 内的脏页刷盘**（flush_log_before_page_write + write_page）：写的是旧 page_id 对应的磁盘位置，不修改 page_table_/free_list_/pages_[] 的结构关系。flush 和 write 是 I/O 操作，耗时可能是内存操作的 100-1000 倍。

2. **`disk_manager_->read_page`**：从磁盘读入数据填充已分配好的 frame，不访问 page_table_ 等共享结构。

这两处 I/O 在锁内意味着**一个线程在等磁盘时，所有其他线程被阻塞**。

## 优化方案

将 `fetch_page` 拆成两段：

```
// 阶段一：锁内 — 只做内存数据结构操作
scoped_lock(latch_)
  page_table_.find()
  replacer_->pin()
  find_victim_page()
  update_page_metadata_only()    ← 精简版：只改 page_table_ + id_，不刷盘
  replacer_->pin() + pin_count_++
解锁

// 阶段二：锁外 — I/O 操作
flush_dirty_page_if_needed()     ← 旧页刷盘（如需要）
disk_manager_->read_page()       ← 读入新页数据
```

**要点**：
- `update_page` 拆分为元数据操作（锁内）和脏页刷盘（锁外）
- `read_page` 移到锁外——frame 已被占，id_ 已指向新 page_id，其他线程不会碰这块 frame
- 锁的临界区从「一次磁盘 I/O 的时间」缩短到「几十次内存操作的时间」

## 预期收益

- **并发度提升**：磁盘 I/O 不再阻塞其他线程的 buffer pool 访问
- **p99 延迟改善**：等待磁盘的线程不再拖慢命中缓存的热路径
- **收益量化待实测**：具体提升取决于磁盘 I/O 延迟占比和并发数

## 风险

- `update_page` 拆分需确保脏页刷盘前旧 page_id 不被其他线程通过 page_table_ 访问到新的脏数据——当前 `update_page` 在写盘前已 erase 旧 page_id，锁外刷盘时该 page_id 已不可达，安全。
- 拆锁后如果 `read_page` 失败（磁盘错误），frame 处于身份已切换但数据未填充的状态——需考虑回滚机制。
