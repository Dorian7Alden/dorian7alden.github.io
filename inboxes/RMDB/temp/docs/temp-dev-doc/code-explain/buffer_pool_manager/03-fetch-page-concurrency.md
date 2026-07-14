# 03 fetch_page 的并发控制：scoped_lock 与锁粒度

本文档讲解 `fetch_page` 中的 `std::scoped_lock` 是什么、保护了什么、以及当前锁粒度过粗的问题。

## std::scoped_lock 是什么

`std::scoped_lock` 是 C++17 引入的 RAII 锁包装器：

- 构造函数里调 `latch_.lock()`（可同时锁多个 mutex，且保证死锁免发）
- 析构函数里调 `latch_.unlock()`
- 离开作用域自动释放，即使中途抛异常也不会漏解锁

```cpp
Page *BufferPoolManager::fetch_page(PageId page_id) {
    std::scoped_lock lock{latch_};  // 加锁，保护整个函数体
    // ... 操作 page_table_、pages_、free_list_ ...
}  // lock 析构，自动解锁
```

等价于手动写 `latch_.lock()` + 函数末尾 `latch_.unlock()`，但更安全——如果中间 `return` 或抛异常，手动写法可能漏解锁。

## latch_ 是什么

`latch_` 是 `BufferPoolManager` 的全局互斥锁（`std::mutex`），定义在 `buffer_pool_manager.h`。它保护的共享数据结构：

| 成员 | 被哪些操作读写 |
|------|--------------|
| `page_table_` | fetch_page / new_page 读写，delete_page / update_page 删 |
| `pages_[]` | fetch_page / new_page 修改 pin_count_，update_page 改 id_ |
| `free_list_` | find_victim_page 弹出，delete_page 压入 |
| `replacer_` | pin / unpin / victim，内部维护淘汰状态 |

## 当前锁粒度问题

当前 `fetch_page` 的锁覆盖了整个函数，包括磁盘 I/O：

```
scoped_lock 作用域：
  ├── page_table_.find()          // 需要锁
  ├── replacer_->pin()            // 需要锁
  ├── find_victim_page()          // 需要锁
  ├── update_page()               // 需要锁
  ├── disk_manager_->read_page()  // ⚠ 不需要锁！纯磁盘操作
  └── replacer_->pin() + pin_count_++ // 需要锁
```

`read_page` 是纯磁盘 I/O，不访问任何 `latch_` 保护的成员。但它被包含在锁作用域内，导致**全 buffer pool 在这段时间被串行阻塞**——线程 A 在等磁盘读完 page 5 的同时，线程 B 想拿已经在内存中的 page 8 也要排队等锁。

## 示意：为什么锁 I/O 是浪费

```
时间 →

当前（read_page 在锁内）：
  线程A: [加锁][查表][淘汰][read_page等待磁盘...][解锁]
  线程B:                                     [加锁][查表(命中!)][返回][解锁]
  线程C:                                               [加锁][查表][淘汰][...

优化后（read_page 在锁外）：
  线程A: [加锁][查表][淘汰][解锁][read_page等待磁盘...]
  线程B:      [加锁][查表(命中!)][返回][解锁]
  线程C:            [加锁][查表][淘汰][解锁][read_page...]
```

注意优化后线程 B 和 C 在 A 等待磁盘期间就能完成操作，不需要排队。

## 总结

| 点 | 说明 |
|----|------|
| scoped_lock 的作用 | RAII 自动管理锁，保护 page_table_ / pages_ / free_list_ / replacer_ |
| 当前问题 | 锁覆盖了磁盘 I/O（read_page），这把锁是全局的，阻塞所有并发操作 |
| 优化方向 | 将 read_page 移到锁外，锁只保护内存数据结构的操作 |
