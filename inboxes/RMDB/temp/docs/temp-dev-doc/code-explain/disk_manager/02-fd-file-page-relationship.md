# 02-fd-file-page-relationship.md

## 问题

DiskManager 中，一个 fd 是否对应磁盘中的一个真实文本文件？一个 fd 下面是否有多个 Page？

## fd 与磁盘文件：一对一

一个 fd 就是操作系统中一个真实的磁盘文件。在 RMDB 中具体有两个来源：

- **数据文件**：每张表在磁盘上对应一个文件。`RmManager::create_file(filename)` → `DiskManager::create_file(filename)` → `open(filename, O_CREAT | O_RDWR)`，在数据库目录下创建真实文件，然后 `open_file` 获取 fd。
- **WAL 日志文件**：`db.log`，单例文件，`log_fd_` 专门持有。

fd 通过 `path2fd_` 和 `fd2path_` 两个哈希表做双向映射，文件名与 fd 一一对应。

## 文件与 Page：一对多

一个文件内部按固定大小的页（Page）组织。`PAGE_SIZE = 4096`（4KB）。文件寻址方式：

```
文件偏移 = page_no × PAGE_SIZE
```

`DiskManager::write_page(fd, page_no, data, num_bytes)` 内部：
```cpp
lseek(fd, page_no * PAGE_SIZE, SEEK_SET);
write(fd, data, num_bytes);
```

所以一个 1MB 的表文件包含 256 个页，一个 100MB 的文件包含 25600 个页。

## 两层索引关系

```
表名/"basic"  ──→ fd (小整数)  ──→ page_no (递增分配)
  path2fd_             fd2pageno_[fd]
  fd2path_             allocate_page(fd)
```

- **文件名 → fd**：`path2fd_` / `fd2path_` 哈希表，按需查询
- **fd → 页号范围**：`fd2pageno_[fd]` 数组，O(1)，记录该文件当前已分配了多少页

每个文件的页号空间独立，都从 0 开始递增分配，互不干扰。
