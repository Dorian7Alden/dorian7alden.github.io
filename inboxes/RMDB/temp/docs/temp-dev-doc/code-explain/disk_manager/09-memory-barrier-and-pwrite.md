# 09-内存屏障与 pwrite/lseek+write 的对比

## 问题

讨论 disk_manager 的性能优化时提出两点：`memory_order_relaxed` 为什么能提升性能？`pwrite` 与 `lseek`+`write` 是否等价，会引发其他问题吗？

## 内存屏障

CPU 为提升性能会乱序执行指令。`std::atomic` 默认使用 `memory_order_seq_cst`（最强一致性），每次 `fd2pageno_[fd]++` 都会插入完整内存屏障（x86 上为 `mfence` 或等效操作），强制等待所有核心的读写操作达到全局一致后才继续。

`memory_order_relaxed` 去掉这道屏障，只保证原子性（不会两个线程同时读到同一个值），不约束周围指令的顺序。

**省掉 `mfence` 有收益，但有限**：一条 `mfence` 代价在几十到上百个时钟周期，但 `allocate_page` 实际调用频率远不如 `write_page`/`read_page`，所以这条优化的真实收益不大。

## 文件偏移行为：实例对比

### 单线程顺序写入

假设 fd 刚打开，文件偏移初始为 0。

```
lseek+write:
  write(fd, bufA, 4096)        → 写偏移 0，fd 偏移自动推进到 4096
  write(fd, bufB, 4096)        → 写偏移 4096，fd 偏移自动推进到 8192
  lseek(fd, 20480, SEEK_SET)   → 跳到 20480（5 号页）
  write(fd, bufC, 4096)        → 写偏移 20480，fd 偏移自动推进到 24576
  write(fd, bufD, 4096)        → 写偏移 24576 ← 上一次 write 停在哪就从哪继续
```

```
pwrite:
  write(fd, bufA, 4096)        → 写偏移 0，fd 偏移自动推进到 4096
  pwrite(fd, bufB, 4096, 8192) → 写偏移 8192，fd 偏移仍是 4096（没变！）
  pwrite(fd, bufC, 4096, 0)    → 写偏移 0，fd 偏移仍是 4096
  write(fd, bufD, 4096)        → 写偏移 4096 ← 继续之前 write 停下的位置
```

**关键差异**：`pwrite` 不碰 fd 的共享偏移。`write` 之后想继续写下一页，不调 `lseek` 也能"顺延"；`pwrite` 每次自己算位置，跳来跳去不影响其他人。

### 多线程写不同页面

线程 A 写 3 号页（偏移 12288），线程 B 写 100 号页（偏移 409600）。

```
lseek+write（共享 fd 偏移，互相踩）：
  时间线 →
  线程 A: lseek(fd, 12288, SEEK_SET)   fd 偏移 = 12288
  线程 B: lseek(fd, 409600, SEEK_SET)  fd 偏移 = 409600  ← 踩掉 A 的位置
  线程 A: write(fd, bufA, 4096)        写到了 409600！  ← 3 号页数据错位
  线程 B: write(fd, bufB, 4096)        写到了 409600    ← 这倒是对的
```

结果：线程 A 的数据错写到 100 号页，3 号页内容丢失，100 号页被 A 和 B 的两次写入先后覆盖，内容不可预测。

```
pwrite（自带偏移，互不依赖）：
  时间线 →
  线程 A: pwrite(fd, bufA, 4096, 12288)   写偏移 12288 ✓ fd 偏移不变
  线程 B: pwrite(fd, bufB, 4096, 409600)  写偏移 409600 ✓ fd 偏移不变
```

结果：各写各的正确位置，互不干扰。

## pwrite 会引发其他问题吗

在 RMDB 场景下不会：

- `pwrite`/`pread` 是 POSIX 标准接口，Linux 完整支持
- 项目已大量使用 POSIX 调用（`lseek`、`stat`、`unlink`、`open`），无移植性风险
- 唯一要求：fd 对应可寻址的普通文件（pipe/socket 不行），磁盘管理器只操作数据文件，满足条件

## 实际验证：改动后测试结果

在独立分支上实施了 `pwrite`/`pread` 替换和 `memory_order_relaxed`，编译零警告，全部 5 个测试套件通过（含 `BufferPoolManagerConcurrencyTest`），与改动前完全一致。

- `pwrite`/`pread` 不仅安全，还从根本上消除了多线程场景下的 TOCTOU 窗口——偏移量作为参数传递而非通过共享 fd 状态
- `memory_order_relaxed` 对纯计数器足够：`allocate_page` 只要求"返回值不重复"，不依赖任何内存排序语义
- `write_log`/`read_log` 保持不动是正确的：`write_log` 依赖 `SEEK_END` 追加（`pwrite` 不支持相对末尾偏移），`read_log` 自行维护顺序偏移读取
