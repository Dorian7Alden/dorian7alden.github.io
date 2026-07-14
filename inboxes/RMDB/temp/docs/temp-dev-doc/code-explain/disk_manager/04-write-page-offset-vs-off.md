# 04-write_page 中 offset 与 off 的区别

## 问题

`disk_manager.cpp:29` 的 `write_page` 方法：

```cpp
void DiskManager::write_page(int fd, page_id_t page_no, const char *offset, int num_bytes)
{
    off_t off = static_cast<off_t>(page_no) * PAGE_SIZE;
    if (lseek(fd, off, SEEK_SET) < 0) throw UnixError();
    ssize_t bytes_written = write(fd, offset, num_bytes);
    if (bytes_written != num_bytes) throw InternalError("...");
}
```

入参 `offset` 和局部变量 `off` 有什么区别？`SEEK_SET` 是什么？

## offset（入参）vs off（局部变量）

| 变量 | 类型 | 含义 |
|------|------|------|
| `offset` | `const char*` | 内存地址指针，指向待写入的数据缓冲区 |
| `off` | `off_t` | 文件偏移量（整数），数据要写到文件的第几个字节位置 |

`off` = `page_no × PAGE_SIZE`，把逻辑页号转换为文件内的字节偏移。例如第 5 号页 → 文件偏移 20480。

`offset` 是内存中数据的起始地址，`write()` 从这里读取 `num_bytes` 字节写入磁盘。

**注意：`offset` 这个命名有误导性——它本质上不是偏移量，而是一个内存指针。** 两个变量长得像，完全是不同的东西：

```
             内存                               磁盘
         offset (指针)                     off (字节偏移)
            │                                  │
            ▼                                  ▼
    ┌───────────────┐                  ┌───────────────┐
    │ 待写入的数据    │  ── write() ──▶  │ 第 N 号页      │
    │ (num_bytes)   │                  │               │
    └───────────────┘                  └───────────────┘
```

- `lseek(fd, off, SEEK_SET)` — 把磁盘写入头移到 `off` 位置（目标位置）
- `write(fd, offset, num_bytes)` — 从内存的 `offset` 地址取出数据写过去

## SEEK_SET

`lseek(fd, off, SEEK_SET)` 把文件读写头定位到从**文件开头**起算的绝对偏移 `off` 处。

`lseek` 有三种定位模式：

| 模式 | 含义 |
|------|------|
| `SEEK_SET` | 从文件开头算起的绝对偏移 |
| `SEEK_CUR` | 从当前读写头位置算起的相对偏移 |
| `SEEK_END` | 从文件末尾算起的相对偏移 |

`write_page` 需要定位到某个页号的精确位置，用绝对偏移 `SEEK_SET` 最直接。

## 整体思路

`write_page` 和 `read_page` 都是同样的两步模式：

1. **定位**：`lseek` 把文件内部读写指针挪到目标页的起始位置（`page_no × PAGE_SIZE`）
2. **读写**：`write` 把内存数据写出去，或 `read` 把磁盘数据读进来

```cpp
void DiskManager::write_page(int fd, page_id_t page_no, const char *offset, int num_bytes) {
    lseek(fd, page_no * PAGE_SIZE, SEEK_SET);  // ① 定位
    write(fd, offset, num_bytes);              // ② 写盘
}

void DiskManager::read_page(int fd, page_id_t page_no, char *offset, int num_bytes) {
    lseek(fd, page_no * PAGE_SIZE, SEEK_SET);  // ① 定位
    read(fd, offset, num_bytes);               // ② 读盘
}
```

两个方法完全对称，只是数据方向相反——`write_page` 内存→磁盘，`read_page` 磁盘→内存。

## 不 lseek 会怎样

内核为每个 fd 维护一个**当前文件位置**，打开文件时初始为 0，每次 `read`/`write` 后自动推进已读写的字节数。

如果不调 `lseek`，读写就从"当前在哪就在哪开始"，依赖之前的操作推进到的位置。如果总按 page_no 顺序读写（0、1、2…），每次恰好推进一页，能"蒙对"。但一旦乱序（BufferPoolManager 淘汰脏页时可能先刷 5 号页再刷 2 号页），不重新 `lseek` 就会写到错误偏移，数据全部错位。

另外，`lseek` + `write` 两步分离，多线程共享同一 fd 时存在 TOCTOU 竞态：

```
线程 A: lseek 到 4096
线程 B: lseek 到 8192    ← 抢走了 A 的位置
线程 A: write             ← 写到了 8192，本应写 4096
```

POSIX 提供了 `pwrite(fd, buf, n, offset)` 可以原子完成"定位+写入"，无需单独 `lseek`。但这个项目没采用，可能是简化考量——实际使用中同一 fd 的并发写由 BufferPoolManager 上层串行化控制。
