# 10-lseek+write 竞态与 allocate_page 并发分析

## 问题

`DiskManager` 的 `lseek+write` 两步分离是否会导致多线程数据错乱？`allocate_page` 在并发场景下是否安全？

## 结论：两个都是理论风险，非真实 bug

### lseek+write 竞态：BPM latch 已串行化

所有可能在同一 fd 上并发的 `write_page`/`read_page` 调用都经过 `BufferPoolManager`，BPM 公开方法全部持有 `std::scoped_lock lock{latch_}`。两个线程并发执行 DML 时，`lseek+write/read` 被 BPM latch 串行执行，不会出现交叉。

以下直接调用（不经过 BPM）虽然无锁，但都在单线程上下文中执行：

| 调用场景 | 并发风险 |
|----------|----------|
| 启动时加载元数据 | 单线程 |
| Recovery 恢复 | 单线程 |
| DDL（建表/删表） | 表级排他锁 |
| Checkpoint | 排他锁，阻止所有普通 SQL |
| Shutdown 关闭文件 | 单线程 |

**风险**：接口不是线程安全的，如果未来有人绕过 BPM 直接调用 `write_page`/`read_page`，竞态真实存在。属于设计脆弱性。

### allocate_page：BPM latch + atomic 双重保护

`allocate_page` 仅从 `BPM::new_page()` 调用，持有 BPM latch。即使没有 `std::atomic`，BPM latch 也已串行化。`std::atomic` 是防御性设计，额外保障。

## 分析中发现的真实问题：RmFileHandle::file_hdr_ 数据竞争

`create_new_page_handle()` 在 BPM latch **释放后**修改 `file_hdr_.num_pages` 和 `file_hdr_.first_free_page_no`：

```cpp
// rm_file_handle.cpp
RmPageHandle RmFileHandle::create_new_page_handle() {
    Page *page = buffer_pool_manager_->new_page(&page_id);  // latch 在此获取并释放
    // 下面两行无锁！
    file_hdr_.num_pages++;                   // 数据竞争
    file_hdr_.first_free_page_no = ...;      // 数据竞争
}
```

多线程并发 insert 可能导致：
- `num_pages` 增量丢失（两个线程都读到旧值再加 1）
- 两个线程分到同一个空闲页（读到相同的 `first_free_page_no`）

同理，`DiskManager::path2fd_`/`fd2path_` 在 `open_file`/`close_file` 中无锁修改，DDL 与 DML 并发时也有风险。
