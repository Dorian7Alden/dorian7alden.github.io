# 01-DiskManager 系统调用与原子操作的优化

## 优化前

### write_page / read_page：两次系统调用

每次页面读写需要先 `lseek` 定位，再 `write`/`read` 操作，两次系统调用：

```cpp
// 优化前
off_t off = static_cast<off_t>(page_no) * PAGE_SIZE;
if (lseek(fd, off, SEEK_SET) < 0) throw UnixError();  // syscall ①
ssize_t bytes_written = write(fd, offset, num_bytes);   // syscall ②
```

此外 `lseek` 修改 fd 的共享文件偏移，多线程并发读写同一 fd 时存在 TOCTOU 竞态：线程 A `lseek` 后被线程 B 的 `lseek` 抢走位置，A 的 `write` 写到错误偏移。

### allocate_page：不必要的强内存序

```cpp
// 优化前
return fd2pageno_[fd]++;  // 默认 memory_order_seq_cst，插入完整内存屏障
```

## 优化后

### write_page / read_page：一次系统调用

使用 POSIX 的 `pwrite`/`pread`，自带偏移参数，一次系统调用完成定位+读写：

```cpp
// 优化后
ssize_t bytes_written = pwrite(fd, offset, num_bytes,
    static_cast<off_t>(page_no) * PAGE_SIZE);
```

`pwrite` 不修改 fd 的共享文件偏移，多线程各自定址，互不干扰。

### allocate_page：放松内存序

```cpp
// 优化后
return fd2pageno_[fd].fetch_add(1, std::memory_order_relaxed);
```

`relaxed` 只保证原子递增（不重号），不要求与其他内存操作有 happens-before 关系。

## 为什么可以提升性能

| 改动 | 优化前 | 优化后 | 收益 |
|------|--------|--------|------|
| 页面读写 | `lseek` + `write/read`，两次 syscall | `pwrite`/`pread`，一次 syscall | 省掉一次系统调用（微秒级），热路径上累积明显 |
| 页号分配 | `seq_cst` 自增，触发 `mfence` | `relaxed` 自增，无屏障 | 省掉完整内存屏障（几十到上百时钟周期） |
| 并发安全 | `lseek`+`write` 两步分离，存在 TOCTOU 窗口 | `pwrite` 自带偏移，线程安全 | 消除潜在竞态 |

## 具体实例：文件偏移行为对比

### 单线程顺序写入

fd 刚打开，内核维护的共享文件偏移初始为 0。

```
lseek+write（共享偏移自动推进）：
  write(fd, bufA, 4096)        → 写偏移 0，fd 偏移自动推进到 4096
  write(fd, bufB, 4096)        → 写偏移 4096，fd 偏移自动推进到 8192
  lseek(fd, 20480, SEEK_SET)   → 跳到 20480（5 号页）
  write(fd, bufC, 4096)        → 写偏移 20480，fd 偏移自动推进到 24576
  write(fd, bufD, 4096)        → 写偏移 24576 ← 上次停哪就从哪继续
```

```
pwrite（不碰共享偏移）：
  write(fd, bufA, 4096)        → 写偏移 0，fd 偏移自动推进到 4096
  pwrite(fd, bufB, 4096, 8192) → 写偏移 8192，fd 偏移仍是 4096（没变！）
  pwrite(fd, bufC, 4096, 0)    → 写偏移 0，fd 偏移仍是 4096
  write(fd, bufD, 4096)        → 写偏移 4096 ← 继续之前 write 停下的位置
```

### 多线程写不同页面（竞态）

线程 A 写 3 号页（偏移 12288），线程 B 写 100 号页（偏移 409600）。

```
lseek+write（共享偏移，互相踩）：
  线程 A: lseek(fd, 12288, SEEK_SET)   fd 偏移 = 12288
  线程 B: lseek(fd, 409600, SEEK_SET)  fd 偏移 = 409600  ← 踩掉 A
  线程 A: write(fd, bufA, 4096)        写到 409600！      ← 3 号页数据错位
```
结果：A 的数据错写到 100 号页，3 号页丢失，100 号页被两次写入先后覆盖。

```
pwrite（自带偏移，互不干扰）：
  线程 A: pwrite(fd, bufA, 4096, 12288)   写偏移 12288 ✓
  线程 B: pwrite(fd, bufB, 4096, 409600)  写偏移 409600 ✓
```
结果：各写各的，互不干扰。

## 为什么不会引发问题

- **关于竞态**：当前架构下，多线程竞态实际不会触发。所有可能在同一 fd 上并发的 `write_page`/`read_page` 调用都经过 `BufferPoolManager`，BPM 公开方法全部持有 `std::scoped_lock lock{latch_}` 串行化。不经过 BPM 的直接调用（启动加载、DDL、recovery、checkpoint）均在单线程或排他锁上下文中执行。因此优化前即使不改为 `pwrite`，竞态也不会真实发生。改为 `pwrite` 主要收益是**减少系统调用次数**，同时消除这个设计脆弱点，防止未来有人绕过 BPM 直接调用时踩坑
- `pwrite`/`pread` 是 POSIX 标准接口（Linux 完整支持），与原有 `lseek`/`write`/`read` 功能等价。唯一差异是不修改 fd 共享偏移，但 `write_page`/`read_page` 每次都显式传入 `page_no` 计算绝对偏移，不依赖共享偏移的自动推进
- `memory_order_relaxed` 对纯计数器完全够用。`allocate_page` 只要求返回值不重复（原子性），不要求调用方通过它的内存序来同步其他数据。上层 BPM latch 已提供必要的同步
- `write_log`/`read_log` 保持不动：`write_log` 依赖 `SEEK_END` 追加模式，`pwrite` 不支持相对末尾的偏移
- 编译零警告，全部 5 个测试套件通过，含并发测试
