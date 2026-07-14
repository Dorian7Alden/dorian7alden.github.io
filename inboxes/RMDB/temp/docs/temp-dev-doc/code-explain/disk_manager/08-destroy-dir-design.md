# 08-目录与文件删除策略的设计选择

## 问题

为什么 `destroy_dir` 用 `system("rm -r")` 而不是 POSIX 的 `rmdir()`？为什么 `rm -r` 不加 `-f`？为什么 `destroy_file` 用 `unlink()` 而 `destroy_dir` 走 shell？

## create_dir / destroy_dir 为什么用 system() 而不是 mkdir() / rmdir()

`system()` 调 shell 命令，自动处理递归删除（`rm -r`）和父目录创建（`mkdir -p`），比纯 POSIX 系统调用方便。代价是效率低、有命令注入隐患。教学代码常见的取舍。

## destroy_dir 为什么用 rm -r 而不加 -f

```cpp
std::string cmd = "rm -r " + path;
```

`-r` 递归删除目录及其内容。没加 `-f`（force）的原因：

- `-f` 会忽略不存在的文件（对不存在的路径也不报错），导致"删了一个不存在的目录"也静默成功。不加 `-f`，目录不存在时 `rm` 返回错误码，能及早发现问题。
- `-f` 会跳过只读文件的确认提示、强制删除无权限文件。在数据库系统里，删除操作最好明确失败而不是静默覆盖，有助于暴露潜在的逻辑错误。
- 调用方应当在删除前确保目录存在且有权操作，用不加 `-f` 的 `rm` 可以起一个"断言"的作用——不该发生的事如果发生了就报错。

## destroy_dir 用 rm -r vs destroy_file 用 unlink()

| 对比 | `destroy_dir` | `destroy_file` |
|------|---------------|----------------|
| 底层调用 | `system("rm -r")` | `unlink()` |
| 调用方式 | shell 命令 | POSIX 系统调用 |
| 处理对象 | 目录树（可含多层子目录和文件） | 单个文件（叶子节点） |
| 前置检查 | 无（靠 `rm` 报错） | `is_file` + `path2fd_` 检查 |

**文件用 `unlink()`**：文件是单个对象，一次系统调用直接移除目录条目。快、安全、无 shell 注入风险。调用前已完成 `is_file` 和 `fd` 状态检查，前置条件充分。

**目录用 `rm -r`**：目录可能包含文件、子目录、嵌套内容。POSIX 的 `rmdir()` 只能删空目录，要递归删除得自己遍历目录树：

```
opendir → readdir → 对每个条目判断：
  ├── 是文件 → unlink
  └── 是目录 → 递归进入后删除 → rmdir
→ rmdir 顶层目录
```

这比 `rm -r` 工作量大得多。交给 shell 处理，一行搞定递归。

总结：文件是叶子，一个 `unlink` 够用；目录是树，让 shell 承包递归。

## 用 rmdir() 替换 rm -r 能提升性能吗

理论上能省掉 fork+exec（约 1~2ms），但实际收益为零。

- `destroy_dir` 只在 DDL 操作（删表、删库）时触发，整个测试周期可能只调用几次，是彻底的冷路径
- 删除操作真正的耗时在磁盘元数据更新，与走 shell 还是走系统调用无关
- 手写递归 `opendir`/`readdir`/`unlink`/`rmdir` 增加十几行代码，维护成本高于一行 `system()`
- 真要做性能优化，应该看 BufferPoolManager 的页面替换和 `allocate_page` 的并发——那些是每秒几十万次的热路径
