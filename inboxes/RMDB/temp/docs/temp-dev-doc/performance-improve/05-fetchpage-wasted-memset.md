# 05-fetch_page 路径上 update_page 的浪费的 memset

**状态**：已识别，待实施。

## 当前状况

`fetch_page` miss 时的调用链：

```
fetch_page (line 48-51)
  → find_victim_page(&frame_id)
  → update_page(page, page_id, frame_id)   // 含 page->reset_memory()
  → disk_manager_->read_page(...)           // 紧接着覆盖整个 data_
```

`update_page` 内部（line 277）：

```cpp
void BufferPoolManager::update_page(Page *page, PageId new_page_id, frame_id_t new_frame_id) {
    // ... 脏页刷盘、page_table_ 更新 ...
    page->reset_memory();  // memset(data_, 0, PAGE_SIZE) — 16KB 清零
    page->id_ = new_page_id;
    page->is_dirty_ = false;
}
```

而 `fetch_page` 紧接着执行：

```cpp
disk_manager_->read_page(page_id.fd, page_id.page_no, page->get_data(), PAGE_SIZE);
// ↑ 从磁盘读 16KB 数据覆盖整个 data_
```

`reset_memory()` 清零的 16KB 在下一行就被 `read_page` 完全覆盖。

## 问题分析

`update_page` 服务于两个调用方：

| 调用方 | 后续操作 | memset 是否有用 |
|--------|----------|----------------|
| `fetch_page` | `read_page` 立即覆盖 | **浪费** — 16KB memset 结果被丢弃 |
| `new_page` | 上层写入数据 | **有用** — 调用方期望拿到全零页 |

`fetch_page` 是热路径（每次 cache miss 都走），miss 频率取决于 buffer pool 大小和工作集。16KB memset 约 100-200ns（取决于 CPU 和内存带宽），每次 miss 多花这些时间。

## 优化方案

给 `update_page` 加一个 `bool skip_reset` 参数，`fetch_page` 路径传 `true` 跳过 memset：

```cpp
// 优化后
void BufferPoolManager::update_page(Page *page, PageId new_page_id, frame_id_t new_frame_id,
                                     bool skip_reset = false) {
    // ... 脏页刷盘、page_table_ 更新 ...
    if (!skip_reset) {
        page->reset_memory();
    }
    page->id_ = new_page_id;
    page->is_dirty_ = false;
}

// fetch_page 调用处：
update_page(page, page_id, frame_id, /*skip_reset=*/true);

// new_page 调用处：
update_page(page, *page_id, frame_id);  // 默认 false，保留 memset
```

## 预期收益

- 每次 `fetch_page` miss 省一次 16KB memset（约 100-200ns）
- 纯内存操作优化，不涉及 I/O 或锁变更
- 收益量化待实测

## 为什么安全

- `fetch_page` 在 `update_page` 后立��执行 `read_page`，数据区被完全覆盖
- `new_page` 路径保留 memset，调用方行为不变
- 不影响 `page_table_`、`is_dirty_`、`pin_count_` 等其他状态
- 不影响 `delete_page` 路径（delete_page 不用 update_page，自己管理 frame 清理）
