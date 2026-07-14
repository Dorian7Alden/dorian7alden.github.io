# 05 pin_count：引用计数还是使用次数

本文档讲解 `pin_count` 的真正含义——它控制的是"帧能不能被淘汰"，而非"页被访问了多少次"。

## pin_count 是引用计数

`fetch_page` 和 `new_page` 返回 Page* 给调用方时，都会设 `pin_count = 1`。这个 1 不表示"页被用了一次"，而是表示「有 **1** 个调用方持有这张页的指针」。调用方释放引用时调 `unpin_page`，pin_count 减 1。归零意味着没有人再持有引用，帧可以安全淘汰。

```
fetch_page / new_page
      │
      ▼
  pin_count = 1          ← 帧被持有，replacer 不可淘汰
      │
      ▼
  调用方读写 page
      │
      ▼
  unpin_page             ← pin_count--, 归零时 replacer 标记为可淘汰
```

## 为什么返回时就必须置 1

不是因为调用方"一定会读写"，而是因为调用方**持有了指针**。从 `fetch_page` 返回那一刻起，到 `unpin_page` 之前，调用方随时可能通过指针访问 `data_`。如果 pin_count = 0，`find_victim_page` 随时可能把这一帧分配给另一个 page_id——调用方手里的指针就成了悬空指针。

打个比方：借书时登记的不是"承诺会读"，而是"这本书不在架上了，别借给别人"。翻两页就还还是精读三天，是调用方的事——但只要书还在你手上，别人就不能拿走。

## API 契约

| 函数 | pin_count 变化 | 含义 |
|------|---------------|------|
| `fetch_page` | ↑ 1 | 返回指针，调用方持有引用 |
| `new_page` | ↑ 1 | 返回指针，调用方持有引用 |
| `unpin_page` | ↓ 1 | 调用方释放引用；归零时调 replacer_->unpin |
| `delete_page` | 必须为 0 | 有引用时不能删 |

这个契约是单向的：拿指针的人负责还。BufferPoolManager 不管调用方拿指针去干什么——哪怕什么都不干立刻 unpin，也是合法的。

## 与 replacer_->pin/unpin 的关系

`replacer_` 维护的是「哪些帧可以被淘汰」。pin_count 和 replacer 状态同步：

```
pin_count > 0  ←→  replacer_->pin(frame_id)    // 不可淘汰
pin_count = 0  ←→  replacer_->unpin(frame_id)  // 可淘汰
```
