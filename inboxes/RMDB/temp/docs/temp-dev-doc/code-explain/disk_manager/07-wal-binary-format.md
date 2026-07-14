# 07-WAL 日志是二进制格式，无需换行

## 问题

`write_log` 写入日志时，内容有换行吗？需要手动控制换行吗？

## WAL 日志是二进制格式，不是文本

日志文件 `db.log` 存储的是结构化的 `LogRecord` 对象序列化后的二进制数据，不是文本行。

```
LogRecord 对象 → serialize() → 二进制 bytes → log_buffer_ → write_log() → db.log
```

每条日志记录自带长度字段（`log_tot_len`），读取时通过长度定位记录边界，而不是靠换行符分割：

```
db.log → read_log(offset, size) → 二进制 bytes → DeserializeLogRecord() → LogRecord 对象
```

## write_log 只做字节搬运

```cpp
void DiskManager::write_log(char *log_data, int size)
{
    if (log_fd_ == -1) log_fd_ = open_file(LOG_FILE_NAME);
    lseek(log_fd_, 0, SEEK_END);              // 追加到末尾
    ssize_t bytes_write = write(log_fd_, log_data, size);
    if (bytes_write != size) throw UnixError();
}
```

`write_log` 不知道也不关心写入的是什么内容，就是纯粹的 `lseek(SEEK_END)` + `write()` 追加写入。换行符是文本文件的约定，对二进制日志没有意义。

## 读取靠长度字段，不靠换行

`read_log` 按 `offset` + `size` 读取字节块，调用方（`LogManager`）根据 `LOG_HEADER_SIZE` 和 `log_tot_len` 字段逐条切分日志记录。这和文本文件按 `\n` 切行是完全不同的模式。
