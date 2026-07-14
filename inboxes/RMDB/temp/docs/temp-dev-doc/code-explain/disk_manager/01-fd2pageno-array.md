# 01-DiskManager 的 fd2pageno_ 数组

## 问题

`disk_manager.h:99` 的私有字段：

```cpp
std::atomic<page_id_t> fd2pageno_[MAX_FD]{}; // MAX_FD = 8192, page_id_t = int32_t
```

这个字段的数据结构是什么？有什么用途？为什么要加 `std::atomic`？

## 数据结构

固定大小 **8192** 的数组，每个元素是 `std::atomic<int32_t>`。初始值全部为 0（由 `{}` 值初始化保证，构造函数中又用 `memset` 再次清零）。

**fd 直接作为数组下标**。这里 fd 是操作系统 `open()` 返回的文件描述符（小整数），不是自定义索引，因此数组大小 8192 对应进程最大可打开文件数。fd 作下标意味着无需额外哈希查找，直接 `O(1)` 下标访问。

**MAX_FD 并不等于 OS 保证的 fd 上限**。操作系统不会以 8192 为限返回 fd —— Linux 默认单进程软限制通常是 1024（`ulimit -n`），但可以调到远大于 8192。代码唯一的防护是 `allocate_page` 中的 `assert(fd >= 0 && fd < MAX_FD)`，release 模式下会被编译掉，所以实际上没有运行时保护。这个常数只是一个"够大就行"的工程假设：项目内每个表/索引各占一个 fd，总数远小于 1024，不可能撞到 8192 的上限。

与之对比，`path2fd_` 和 `fd2path_` 是 `unordered_map`，用于 fd 和文件路径之间的双向映射，那是按需查询的。而 `fd2pageno_` 用数组是因为 `allocate_page` 在热路径上（每次新建页面都要调用），必须**极快**。

## 用途：页号分配器

每个数据文件（表、索引等）各自有独立的页号空间，从 0 开始递增分配。`fd2pageno_[fd]` 记录文件 fd **已经分配了多少页**，同时也是**下一个待分配的页号**。

`allocate_page` 的实现只有一行：

```cpp
// disk_manager.cpp:73
return fd2pageno_[fd]++;
```

这是"后置自增"：返回当前值，然后 +1。所以文件第一个分配的页是 0 号页，分配后计数器变为 1，下一次分配得到 1 号页，依此类推。

调用方（BufferPoolManager）用这个返回值作为页号，通过 `write_page(fd, page_no, ...)` 定位到文件偏移 `page_no * PAGE_SIZE` 处读写。

## 为什么用 std::atomic

`fd2pageno_[fd]++` 是一次**读-改-写**操作：

1. 读出当前值（如 5）
2. 返回旧值（5）给调用方
3. 写入新值（6）

如果不用 atomic，两个线程并发为同一个文件分配页面：

```
线程 A: 读 → 5
线程 B: 读 → 5     ← 在线程 A 写入 6 之前就读了
线程 A: 写 → 6
线程 B: 写 → 6     ← 也是 6，5 被分配了两次
```

两个线程都拿到 5 号页，6 号页被跳过。两个页面写同一个物理位置，数据互相覆盖。

`std::atomic` 保证 `++` 的读-改-写是**不可分割的**：线程 A 完成整个自增后线程 B 才看到新值，每个页号只被分配一次。

## 补充：memset 的安全性

构造函数中用 `memset` 清零 atomic 数组：

```cpp
memset(fd2pageno_, 0, MAX_FD * (sizeof(std::atomic<page_id_t>) / sizeof(char)));
```

这依赖 `std::atomic<int32_t>` 是 **lock-free** 且内存布局与 `int32_t` 相同，memset 才是安全的。在 x86/ARM 上 `std::atomic<int32_t>` 确实满足这两个条件（标准保证 `std::atomic<int32_t>::is_always_lock_free` 为 true）。

## 补充：MAX_FD 是否可以缩小来提升性能

不能。数组总大小仅 **32KB**（`8192 × 4 字节`），比 L1 数据缓存还小。访问始终是单下标索引 `fd2pageno_[fd]`，不遍历不搜索，寻址开销恒为 `基址 + fd × 4`，与数组大小无关。即便把上限砍到 1024 省下 ~28KB 内存，在毫秒级的热路径上也感知不到任何差异。
