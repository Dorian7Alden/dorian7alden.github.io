# disk_manager

对 `src/storage/disk_manager.cpp` 及其头文件的源代码讲解。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `01-fd2pageno-array.md` | fd2pageno_ 数组：数据结构、用途、为什么用 atomic |
| `02-fd-file-page-relationship.md` | fd 与磁盘文件及 Page 的对应关系 |
| `03-memset-sizeof-char.md` | memset 中除以 sizeof(char) 的原因 |
| `04-write-page-offset-vs-off.md` | write_page 中 offset（内存指针）与 off（文件偏移）的区别，SEEK_SET 的含义 |
| `05-attribute-unused-stub.md` | 空函数体桩函数、__attribute__((unused)) 的作用 |
| `06-stat-file-operations.md` | stat()、S_ISDIR、S_ISREG、get_file_size 的 rc 约定 |
| `07-wal-binary-format.md` | WAL 日志是二进制格式，无需换行，靠 log_tot_len 字段分界 |
| `08-destroy-dir-design.md` | 目录/文件删除策略：system() vs POSIX、rm -r 不加 -f、rm -r vs unlink |
| `09-memory-barrier-and-pwrite.md` | 内存屏障的含义、pwrite vs lseek+write 等价性与风险 |
| `10-race-analysis.md` | lseek+write 竞态和 allocate_page 并发的实际影响分析 |
