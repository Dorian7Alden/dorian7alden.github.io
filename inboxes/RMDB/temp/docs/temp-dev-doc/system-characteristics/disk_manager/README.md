# disk_manager 特性

## fd2pageno_ 数组大小

- **值/范围**：MAX_FD = 8192，数组占用 32KB
- **性质**：静态推导
- **来源**：`disk_manager.h:91`，`config.h:36 PAGE_SIZE=4096`
- **优化关联**：32KB 完全在 L1 缓存内，fd 直接当下标 O(1)；缩小无性能收益

## fd 实际范围

- **值/范围**：通常 3 ~ 100（每个表/索引/日志各占一个 fd）
- **性质**：静态推导
- **来源**：`open_file()` 返回操作系统分配的小整数
- **优化关联**：fd << 16 对哈希分布影响微弱，因为 fd 值域极小；改用 std::hash 打散更有效

## page_no 碰撞阈值

- **值/范围**：page_no ≥ 65536 时触发 `(fd << 16) | page_no` 哈希碰撞
- **性质**：静态推导
- **来源**：`page.h:33 Get()` 位运算分析；65636 × 4KB = 256MB
- **优化关联**：单表文件超过 256MB 时 page_table_ 查找退化链表

## 页分配方式

- **值/范围**：`fetch_add(1, relaxed)`，从 0 开始递增，不回收
- **性质**：静态推导
- **来源**：`disk_manager.cpp:65`
- **优化关联**：page_no 严格递增，同一文件内无碎片；无需 relaxed 以上的内存序

## 页面读写 syscall 次数

- **值/范围**：每次读写 1 次 syscall（pwrite/pread）
- **性质**：静态推导（已优化）
- **来源**：`disk_manager.cpp:32,49`
- **优化关联**：当前已是最优；`write_log` 仍用 lseek+write（SEEK_END 需求），无需改动

## 目录操作开销

- **值/范围**：create_dir/destroy_dir 走 system()，fork+exec 约 1~2ms
- **性质**：静态推导
- **来源**：`disk_manager.cpp:86-98`
- **优化关联**：DDL 冷路径，收益为零，不优化

## 文件删除方式

- **值/范围**：文件用 unlink()（直接 syscall），目录用 rm -r（shell 递归）
- **性质**：静态推导
- **来源**：`disk_manager.cpp:128-131,94`
- **优化关联**：文件删除已最优；目录删除走 shell 足够
