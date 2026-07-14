# buffer_pool_manager

对 `src/storage/buffer_pool_manager.h` 的源代码讲解。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `01-pool-size-and-page-array.md` | pool_size_ 是帧个数而非字节数之和，pages_ = new Page[pool_size_] 的原理和 256MB 的来历 |
| `02-page-eviction-flow.md` | update_page 的帧身份切换流程、flush_log_before_page_write 的 WAL 协议、reset_memory 的必要性、fetch_page/new_page 两种调用路径的差异 |
| `03-fetch-page-concurrency.md` | std::scoped_lock 的作用、latch_ 保护的共享数据、当前锁覆盖磁盘 I/O 的粒度过粗问题 |
| `04-new-page-function.md` | new_page 的完整流程、page_id 的 in/out 语义（fd 入、page_no 出）、与 fetch_page 的对比 |
| `05-pin-count-lifecycle.md` | pin_count 是引用计数而非使用次数、为什么返回指针就必须置 1、与 replacer_ 的同步关系 |
