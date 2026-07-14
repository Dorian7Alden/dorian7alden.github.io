# 06-stat()、S_ISDIR 等文件/目录操作的讲解

## 问题

DiskManager 中 `is_dir`、`is_file` 等函数用到的 `stat()`、`S_ISDIR`、`S_ISREG` 是什么？文件和目录操作的底层调用各是什么？

## stat()：获取文件元信息

POSIX 系统调用，把路径传给内核，内核填充一个 `struct stat` 结构体：

```cpp
struct stat st;
int rc = stat(path.c_str(), &st);
// rc == 0  成功
// rc < 0   失败（不存在、权限不够等）
```

`stat` 结构体的关键字段：

| 字段 | 含义 |
|------|------|
| `st_mode` | 文件类型 + 权限位，用宏解析 |
| `st_size` | 文件大小（字节） |

## S_ISDIR / S_ISREG：文件类型判断宏

都是宏，检查 `st_mode` 中的类型位：

```cpp
S_ISDIR(st.st_mode)   // 是不是目录
S_ISREG(st.st_mode)   // 是不是普通文件
S_ISLNK(st.st_mode)   // 是不是符号链接（项目中没用到）
```

`is_dir` 的逻辑 = "存在 + 是目录"：

```cpp
return stat(path.c_str(), &st) == 0 && S_ISDIR(st.st_mode);
```

## get_file_size：rc 与返回值约定

```cpp
int DiskManager::get_file_size(const std::string &file_name)
{
    struct stat stat_buf;
    int rc = stat(file_name.c_str(), &stat_buf);
    return rc == 0 ? stat_buf.st_size : -1;
}
```

`rc`（return code）是 `stat()` 的返回值。POSIX 系统调用的惯例：**返回 0 表示成功，-1 表示失败**。

- `rc == 0`：文件存在且可访问，`stat_buf` 已被内核填充，`st_size` 是文件大小（字节）
- `rc == -1`：文件不存在或无权限，返回 `-1` 作为错误标记

参数名 `file_name` 和 `is_file`/`is_dir` 的 `path` 是同一回事，都是文件系统路径字符串，只是命名不统一，无功能差异。

## 项目中所有文件/目录操作一览

| 操作 | 函数 | 底层调用 | 说明 |
|------|------|----------|------|
| 判断目录存在 | `is_dir` | `stat` + `S_ISDIR` | 两条件同时满足 |
| 判断文件存在 | `is_file` | `stat` + `S_ISREG` | 两条件同时满足 |
| 创建目录 | `create_dir` | `system("mkdir ...")` | 调 shell 命令 |
| 删除目录 | `destroy_dir` | `system("rm -r ...")` | 调 shell 命令 |
| 创建文件 | `create_file` | `open(O_CREAT)` | 创建空文件后立即 `close` |
| 删除文件 | `destroy_file` | `unlink` | POSIX 删除文件的标准调用 |
| 获取文件大小 | `get_file_size` | `stat` → `st_size` | 失败返回 -1 |
