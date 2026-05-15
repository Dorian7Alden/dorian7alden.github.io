---
create-time: 2026-05-14
update-time: 2026-05-14
---



## 在 Windows 中通过 WSL 使用 Ubuntu 



### 快速启动 Ubuntu 终端



1. 将 Ubuntu 设置为默认的终端

![image-20260514195128427](https://gitee.com/Seniorsy/pic-go/raw/master/typora/image-20260514195128427.png)

2. 使用快捷指令打开： `win+R` 启动快捷启动程序，然后输入 `wt` （windows terminal 猜的简写），打开默认终端，即可通过快捷键启动 Ubuntu 终端系统



### 使用经验



#### Ubuntu 访问 Windows 中的文件路径



Ubuntu 访问 Windows 的文件路径的时候，需要加上文件路径前缀 `/mnt/` ，并且盘符变成了目录路径，盘符为小写。

例如：`/mnt/c/users/`



#### 在 Ubuntu 中通过指令打开 Windows 文件管理器



在命令行终端中，执行 `explorer.exe .` 可以打开以当前文件路径为基准的 Windows 文件管理器。

![image-20260514195753517](https://gitee.com/Seniorsy/pic-go/raw/master/typora/image-20260514195753517.png)





