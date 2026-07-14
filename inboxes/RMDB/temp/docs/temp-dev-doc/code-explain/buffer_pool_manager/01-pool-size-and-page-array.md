# 02-pool_size_ 是帧个数还是字节数之和？

## 问题

`BufferPoolManager` 构造函数中：

```cpp
pages_ = new Page[pool_size_];
```

`pool_size_` 到底是 BufferPool 中所有 Page 的数据大小之和（字节数），还是 Page 对象的个数？

## 先分清两个概念："页"和"帧"

RMDB 的 Page 对象在磁盘上有文件存储（通过 `DiskManager` 读写），在内存中有对应的缓存位置。这两个位置用不同词称呼：

| | 在哪 | 用什么标识 |
|---|---|---|
| **页** (page) | 磁盘上的数据块 | `PageId {fd, page_no}` — 文件描述符 + 页内编号 |
| **帧** (frame) | BufferPool 中的槽位 | `frame_id_t` — `pages_` 数组的下标 |

一帧对应一页，所以一个 Page 对象同时承载着"磁盘上的身份"（`id_`）和"内存中的数据"（`data_`）。

## 涉及的常量

```cpp
// src/common/config.h
static constexpr int PAGE_SIZE = 4096;          // 每页数据区大小 4KB
static constexpr int BUFFER_POOL_SIZE = 65536;  // buffer pool 大小，即帧个数
// 注释写 "size of buffer pool 256MB" 是因为:
//   65536 帧 × 4096 字节/帧 = 268,435,456 bytes = 256 MB
// 另一行被注释掉的备选值:
// static constexpr int BUFFER_POOL_SIZE = 262144;  // 1GB

using frame_id_t = int32_t;   // 帧 id 类型，范围 0 ~ pool_size_-1
using page_id_t = int32_t;    // 页 id 类型
```

```cpp
// src/storage/buffer_pool_manager.h
size_t pool_size_;   // buffer_pool 中可容纳页面的个数，即帧的个数
Page *pages_;        // Page 对象数组，大小为 pool_size_
```

## Page 对象的实际大小

一个 `Page` 对象不是恰好 4096 字节。`PAGE_SIZE` 只是数据区 `data_` 的大小：

```
Page 对象内存布局（典型 64 位系统，有对齐）
┌──────────────────────────────────────┐
│  PageId id_                          │  int fd (4B) + page_id_t page_no (4B) = 8B
├──────────────────────────────────────┤
│  char data_[4096]                    │  4096B — 页的实际数据区
├──────────────────────────────────────┤
│  bool is_dirty_                      │  1B
│  (padding 3B)                        │  对齐到 4B
├──────────────────────────────────────┤
│  int pin_count_                      │  4B
└──────────────────────────────────────┘
总共约 4112 字节/对象（具体取决于编译器和平台的对齐）
```

`PAGE_SIZE` 只是 `data_` 数组的长度，不是 `sizeof(Page)`。`pages_` 数组实际占用的内存 = `pool_size_ × sizeof(Page)`，比 256MB 略大一点。

## 构造函数做了什么（完整序列）

```cpp
BufferPoolManager(size_t pool_size, DiskManager *disk_manager)
    : pool_size_(pool_size), disk_manager_(disk_manager)
{
    // ① 预分配连续 Page 数组
    pages_ = new Page[pool_size_];

    // ② 创建淘汰策略（当前只用了 LRU，CLOCK 的 if 分支也返回 LRU）
    replacer_ = new LRUReplacer(pool_size_);

    // ③ 所有帧初始时都是空闲的，帧号写入 free_list_
    for (size_t i = 0; i < pool_size_; ++i) {
        free_list_.emplace_back(static_cast<frame_id_t>(i));
    }
}
```

### ① `new Page[pool_size_]` — 一次性预分配所有帧

```
pages_ 数组 (pool_size_ = 65536 个连续的 Page 对象)
┌──────────────────────────────────────────────────────────────────┐
│ Page[0]           Page[1]           Page[2]    ...    Page[65535]│
│ ┌──────────────┐  ┌──────────────┐                              │
│ │ data_[4096]  │  │ data_[4096]  │  每个 Page 在构造时自动调用   │
│ │ id_ = {0,-1} │  │ id_ = {0,-1} │  Page() { reset_memory(); }  │
│ │ is_dirty_=F  │  │ is_dirty_=F  │  将 data_ 全部清零           │
│ │ pin_count_=0 │  │ pin_count_=0 │                              │
│ └──────────────┘  └──────────────┘                              │
└──────────────────────────────────────────────────────────────────┘
  ↑ 帧 0             ↑ 帧 1             ↑ 帧 2           ↑ 帧 65535
```

`new Page[N]` 会调用每个元素的**默认构造函数**。`Page::Page()` 中调用 `reset_memory()`：

```cpp
void reset_memory() { memset(data_, OFFSET_PAGE_START, PAGE_SIZE); }
// 等价于 memset(data_, 0, 4096)
```

所以数组创建后，所有帧的 `data_` 已经全是零，`is_dirty_` 默认 `false`，`pin_count_` 默认 0，`id_` 中 `page_no` 初始化为 `INVALID_PAGE_ID (-1)`。

### ② Replacer 也拿到 `pool_size_`

`LRUReplacer(pool_size_)` 需要知道总共有多少个帧，才能管理哪些帧可被淘汰、哪些被 pin 住不能淘汰。

### ③ `free_list_` — 空闲帧的登记表

```
初始化后的 free_list_:
┌───┬───┬───┬─────┬───────┐
│ 0 │ 1 │ 2 │ ... │ 65535 │   ← 所有帧号都在链表中
└───┴───┴───┴─────┴───────┘
```

运行时，分配帧从 `free_list_` 头部取，归还帧从尾部放回。当 `free_list_` 空了，就通过 `replacer_` 找 victim 帧逐出。

## 为什么用数组而不是链表/分别 new？

1. **O(1) 定位**：已知 `frame_id`，直接 `pages_[frame_id]` 访问。如果分别 new，需要额外指针数组或 map 来映射帧号到对象。
2. **连续内存**：CPU 缓存友好。相邻帧的访问可能已经在 cache line 里。
3. **构造/析构简单**：`new Page[N]` 一次分配，`delete[] pages_` 一次释放，没有 N 次 `new`/`delete` 的开销。
4. **帧号就是数组下标**：不需要额外的映射层。`free_list_` 里存的 `frame_id_t` 天然可以直接做下标。

```
frame_id = 42  →  pages_[42]   // 指针算术，一条指令
```

## 帧的分配与归还

```
初始状态:
  free_list_: [0, 1, 2, ..., 65535]   ← 全在空闲链表
  replacer_:  空（没有活跃帧）

fetch_page({fd:3, page_no:5}):
  → 从 free_list_ 取帧 0
  → pages_[0].id_ = {3, 5}，从磁盘读入 data_
  → replacer_ 记录帧 0 被访问

fetch_page({fd:3, page_no:8}):
  → 从 free_list_ 取帧 1
  → pages_[1].id_ = {3, 8}，从磁盘读入 data_

unpin_page({fd:3, page_no:5}, false):
  → pages_[0].pin_count_--，变成 0
  → replacer_ 标记帧 0 可淘汰

再次 fetch 且 free_list_ 空:
  → replacer_ 找 victim → 帧 0
  → 如果帧 0 是脏页，先刷盘
  → pages_[0].id_ 改为新页，读入新数据
```

## 析构函数的对称性

```cpp
~BufferPoolManager() {
    delete[] pages_;    // 与 new Page[pool_size_] 配对
    delete replacer_;   // 与 new LRUReplacer(pool_size_) 配对
}
```

## 256MB 到底是怎么来的

```
数据区总容量 = BUFFER_POOL_SIZE × PAGE_SIZE
            = 65536 帧 × 4096 字节/帧
            = 268,435,456 字节
            = 262,144 KB
            = 256 MB
```

这个 256MB 是**所有帧的 `data_` 数组加在一起的大小**。`config.h` 中注释的 "size of buffer pool 256MB" 就是指这个乘积。

`pages_` 数组的实际内存占用略大于 256MB，因为每个 `Page` 对象除了 `data_[4096]` 还有 `id_`、`is_dirty_`、`pin_count_` 等成员。但在日常讨论中，"buffer pool 256MB" 指的就是数据区的总容量。

## 总结

| 符号 | 类型 | 含义 |
|------|------|------|
| `pool_size_` | `size_t` | 帧个数（能同时缓存多少个 Page） |
| `PAGE_SIZE` | `constexpr int` | 每帧数据区大小 = 4096 字节 |
| `BUFFER_POOL_SIZE` | `constexpr int` | `pool_size_` 的默认取值 = 65536 |
| `pages_` | `Page*` | 连续数组，`pages_[i]` 就是第 i 帧的 Page 对象 |
| `free_list_` | `list<frame_id_t>` | 空闲帧号链表，`frame_id_t` 直接是 `pages_` 下标 |
