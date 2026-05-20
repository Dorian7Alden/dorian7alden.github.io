---
create-time: 2026-05-15
update-time: 2026-05-15
---



## linux 环境下默认对中文进行编码



- linux 操作系统使用 `ls` 指令显示中文文件时
- git bash 使用 `git status` 显示文件改动时



### 解决 ls 的中文编码

把环境变量写入你的 shell 配置文件（例如 `~/.bashrc` 或 `~/.profile`）：

```bash
echo 'export LANG=zh_CN.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=zh_CN.UTF-8' >> ~/.bashrc
source ~/.bashrc
```



### 解决 git status 的中文编码

控制台输入：

```bash
git config --global core.quotepath false
```

原因解释：

