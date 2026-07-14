# 04-LRUReplacer 内部冗余锁移除

**状态**：已识别，待实施。

## 当前状况

`LRUReplacer` 的 `victim`、`pin`、`unpin` 三个方法各自持有 `std::scoped_lock{latch_}`：

```cpp
// lru_replacer.cpp
bool LRUReplacer::victim(frame_id_t* frame_id) {
    std::scoped_lock lock{latch_};  // ← 内层锁
    ...
}

void LRUReplacer::pin(frame_id_t frame_id) {
    std::scoped_lock lock{latch_};  // ← 内层锁
    ...
}

void LRUReplacer::unpin(frame_id_t frame_id) {
    std::scoped_lock lock{latch_};  // ← 内层锁
    ...
}
```

而唯一调用方 `BufferPoolManager` 在所有公开 API 入口已经持有全局 `latch_`：

```cpp
// buffer_pool_manager.cpp
Page *BufferPoolManager::fetch_page(PageId page_id) {
    std::scoped_lock lock{latch_};       // ← 外层锁（已持有）
    ...
    replacer_->pin(frame_id);            // ← 内部又加一层锁
    ...
}
```

`Replacer` 没有其他调用方——`BufferPoolManager` 是唯一使用者。内层锁保护的共享数据（`LRUlist_`、`LRUhash_`）在外层锁的串行化下已经不可能被并发访问。

## 问题分析

每次 Replacer 方法调用执行一次无意义的 mutex lock + unlock。具体开销：

| API | 调用哪些 Replacer 方法 | 冗余锁次数 |
|-----|----------------------|-----------|
| `fetch_page` 命中 | `pin` | 1 |
| `fetch_page` miss | `victim` + `pin` | 2 |
| `new_page` | `victim` + `pin` | 2 |
| `unpin_page` (pin_count→0) | `unpin` | 1 |

每次冗余锁是一对 `futex` 操作（无竞争时在用户态完成，约 10-25 个时钟周期），累积效应在热路径上可感知。

## 优化方案

移除 `victim`、`pin`、`unpin` 中的 `std::scoped_lock lock{latch_};` 行，同时删除 `std::mutex latch_` 成员变量声明。

改动范围：仅 `lru_replacer.cpp` 3 行 + `lru_replacer.h` 1 行。

```cpp
// 优化后 — lru_replacer.cpp
bool LRUReplacer::victim(frame_id_t* frame_id) {
    // std::scoped_lock lock{latch_};  ← 移除
    if (LRUlist_.empty() || frame_id == nullptr) return false;
    *frame_id = LRUlist_.back();
    LRUlist_.pop_back();
    LRUhash_.erase(*frame_id);
    return true;
}
```

## 预期收益

- 每次 Replacer 调用省一对 mutex lock/unlock（无竞争时 ~25 cycles，有竞争时更多）
- fetch_page 命中快速路径：锁操作从 2 对降为 1 对
- 收益量化待实测

## 为什么安全

- BufferPoolManager 是 Replacer 的唯一调用方
- BPM 所有公开 API 在调用 Replacer 之前已持有 `latch_`
- BPM 的内部辅助函数（find_victim_page）不加锁，但它们的调用方（顶层 API）已持锁
- 不存在其他线程绕过 BPM 直接调用 Replacer 的路径
- Replacer 方法之间不存在从不同调用方并发进入的场景
