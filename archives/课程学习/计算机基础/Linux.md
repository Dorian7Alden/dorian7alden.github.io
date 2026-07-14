【黑马程序员新版Linux零基础快速入门到精通，全涵盖linux系统知识、常用软件环境部署、Shell脚本、云平台实践、大数据集群项目实战等】https://www.bilibili.com/video/BV1n84y1i7td?p=30&vd_source=b6e1ca78539fba73d35a26224eac9099



# vim指令



## 指令

- `:wq` 保存并退出
- `:q` 退出
- `:` 尾行模式
- `:set number` 显示行号  | `set nu` 缩写
- `:set nonumber` 关闭行号
- 插入指令
  - insert
    - i --> 当前字符的前面
    - I --> 行首
  - append
    - a --> 当前字符的后面
    - A --> 行尾
  - open
    - o --> 当前字母的下一行开始
    - O --> 上一行

- `yy` --> `Ctrl+C` 
- `p` --> `Ctrl+V` 
- `dd` --> `Ctrl+X` 
  - 技巧：先输入一个数字再输入 `yy` | `p` | `dd` 就是多行操作
- `^` --> 跳到行首
- `$` --> 跳到行尾



- `Ctrl+f` forward 向下翻页
- `Ctrl+b` backward 向上翻页
- `Ctrl+u` up 向下半页
- `Ctrl+d` down 向上半页
- `G` 跳转到文件的最后一行 
- `gg` 跳转到文件的首行
-  `number+G` 跳转到指定行    `:number` 跳转到指定行



- 查找内容
  - `/contents` 向下查找
  - `?contents` 向上查找
  - `n` 跳到查找的下一个 next
  - `N` 跳到查找的上一个
  - `/hello\c` 忽略大小写匹配字符

:set ic	全局忽略大小写	ignore case

替换内容 `line1,line2+s/old/new/g` line1起始行号	line2结尾行号	s表示替换	old需要替换的内容	new替换后的内容	g表示选中的所有old	没有g仅替换第一个	没有line直接s表示当前行

u --> Ctrl+Z undo

vi .vimrc 打开配置文件

# terminal

- `cat file.txt` 查看文件内容  





```shell
rpm -qa | grep mysql
```

- rpm 软件包管理工具 Red Hat Package Manager
  - -q 为查询
- -a 为所有
- | 为将上一个指令的输出作为输出传递给下一个指令
- grep 为文本搜索工具 Global Regular Expression Print 全局正则表达式打印 g/re/p







# 基础指令







## ls

> list

```shell
ls [-a -l -h] [path]
```

- `-a`：all。列出所有文件（隐藏文件[通常以`.`开头的文件跟文件夹]）
- `-l`：list。以列表的形式输出。默认是平铺的形式输出
- `-h`：易于阅读的形式输出文件的大小。（携带文件大小单位k、G，默认为bytes）





## cd

> Change Directory

```shell
cd [path]
```

- 直接执行的时候，返回到默认用户的home目录





## pwd

> Print Work Directory

```shell
pwd
```





## mkdir

> Make Directory

```shell
mkdir [-p] path
```

- `-p`：parent。自动创建不存在的父目录。适用于创建连续多层级的目录





## touch

> 修改文件的时间戳（创建文件）

```shell
touch path
```





## cat

> concatenate查看文件所有内容

```shell
cat path
```





## more

> 查看文件内容。支持翻页

```shell
more path
```

- 按`b`向上翻页-back
- 按`space`向下翻页
- 按`Enter`向下滚动一行
- 按`q`退出-quit





## less

> more的plus版本

```shell
less path
```

- 按 **PageUp 键** 向上翻一页
- 按 **PageDown 键** 向下翻一页
- 按 **↑ 或 ↓ 箭头键** 逐行滚动
- 按 **q 键** 退出





## cp

> copy复制文件/文件夹

```shell
cp [-r] from_path to_path
```

- `-r`：用于复制文件夹。递归复制文件夹





## mv

> move移动文件/文件夹

```shell
mv from_path to_path
```

- 如果目标不存在，则进行改名，确保目标存在。（重命名文件名）





## rm

> remove删除文件/文件夹

```shell
rm [-r -f] *path
```

- `-r`：用于删除文件夹
- `-f`：force。强制删除。（root管理员删除内容会有弹窗提示，-f不会弹窗）
- 一次删除多项内容用空格隔开

- 支持通配符：`\*` 





## which

> 查找命令程序的储存位置

```shell
which cmd
```





## find

> 搜索文件

- 根据文件名搜索

```shell
find from_folder -name "to_file"
```

- 根据文件大小搜索

```shell
find from_folder -size +|-n[kMG]
```



- 支持通配符：`*` 

- +、-表示大于和小于
- n表示大小数字
- kMG表示大小单位
  - k == KB
  - M == MB
  - G == GB
- 例子：查找大于1GB的文件：`find / size +1G` 



## grep

>  Global Regular Expression Print：从文件中过滤文件行

```shell
grep [-n] keyword path
```

- `-n`：显示找到的内容对应的行号
- keyword：用字符串包围起来
- path：文件路径





## wc

> Word Count：统计文件的行数、单词数量等

```shell
wc [-c -m -l -w] path
```

- `-c`：characters统计bytes数量
- `-m`：multi-byte characters统计字符数量
- `-l`：lines统计行数
- `-w`：words统计单词数量
- `-L`：Longest line统计最长行的字符数





## |

> 管道符：将管道符左边命令的结果作为右边命令的输入。

```shell
cat itheima.txt | grep "itheima"
ls -l | grep "test"
```







## echo

> 输出指定的内容

```shell
echo text
```

- 双引号包围
- 输出命令的执行结果用\`\`包围起来。
  - 示例：
    - echo \`pwd\` ，输出：/home/senior 
    - echo pwd，     输出：pwd

- 使用管道符进行传入参数无效





\> 跟 \>>

> 重定向符

```shell
echo "hello world" > test.txt
echo "hello linux" > test.txt
echo "hello world" >> test.txt
```

- \>，将左侧命令的结果，**覆盖**写入到符号右侧指定的文件中
- \>>，将左侧命令的结果，**追加**写入到符号右侧指定的文件中





## tail

> 查看文件的尾部内容，追踪文件的最新更改

```shell
tail [-f -num] path
```

- `-f`：表示持续追踪
- `-num`：查看尾部的函数。默认10行。num是一个数字变量





## su和exit

> switch user切换用户

```shell
su [-] [account]
```

- `-`：是否在切换用户后加载环境变量（建议带上）
- `account`：用户名，默认为root用户



## sudo

> 临时以root的身份执行命令

```shell
sudo cmd
```

- 使用前需要为普通用户配置sudo认证
- 添加sudo认证：
  - 切换到root用户，执行`visudo`命令，打开文件`/etc/sudoers` 
    - 在文件末尾添加`account_name All=(ALL)	NOPASSWD: ALL`
    - 保存退出即可

















# 

# vim指令

> visual interface
>
> vim是vi的增强版。vim兼容所有的vi指令

- 命令模式
  - 以命令驱动功能
- 输入模式
  - 编辑文件内容
- 底线命令模式
  - 以`:`快开始，通常用于文件的保存、退出

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250901193845384.png" alt="image-20250901193845384" style="zoom:67%;" />









# 

# 权限





## 用户和用户组

> 以root用户执行



## 创建用户组

```shell
groupadd group_name
```





## 删除用户组

```shell
groupdel group_name
```





## 创建用户

```shell
useradd [-g -d] user_name
```

- `-g`：指定用户的组（组已经存在）。不指定的话自动加入（同名的用户必须指定组）
- `-d`：指定用户HOME路径。默认在：/home/user_name



## 删除用户

```shell
userdel [-r] user_name
```

- `-r`：删除用户的HOME目录。默认不删除





## 查看用户所属组

```shell
id [user_name]
```

- 默认查看当前用户所属组





## 修改用户所属组

```shell
usermod -aG user_group user_name
```





## 查看所有用户和用户组

```shell
getent password
```

- 信息组成：用户名：密码（x）：用户ID：组ID：描述信息：HOME目录：执行终端（默认bash）



```shell
getent group
```

- 信息组成：组名称：组认证（x）：组ID





## 

## 权限控制解读



- 共10个槽位
  - 槽位1（数据类型）：`- d l` 
    - `-`：表示文件
    - `d`：表示文件夹
    - `l`：表示软连接
  - 槽位2-4（所属用户权限）：`r w x | -` 
  - 槽位5-7（所属用户组权限）：`r w x | -` 
  - 槽位8-10（其他用户权限）：`r w x | -` 
- 权限解释（rwx）
  - `-`：表示无权限
  - 在文件中：
    - r：读取（查看）文件
    - w：写入（修改）文件
    - x：执行（运行）文件
  - 在文件夹中：
    - r：查看文件夹内容（ls命令）
    - w：创建、删除、重命名等操作
    - x：可以更改工作目录到此文件夹（cd命令）

![image-20250901204126209](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250901204126209.png)





## chmod命令

> 修改文件、文件夹的权限
>
> 注意：只有文件、文件夹的所属用户或root用户可以修改

```shell
chmod [-R] 权限 文件或文件夹
```

- `-R`：对文件夹内的全部内容应用同样的操作
- 权限（重置模式）：
  - `u=rwx`：所属用户权限
  - `g=rw`：所属组权限
  - `o=r`：其他用户权限
- 示例：`chmod -R u=rwx,g=rx,o=x test` 

- 快捷方法（三个数字）：

  - 使用方法：`chmod 751 test.txt` 一个数字表示一个权限类型

  - 快速记忆：r=4，w=2，x=1，有几个加几即可

  - |      |      |
    | :--: | :--: |
    |  0   | ---  |
    |  1   | --x  |
    |  2   | -w-  |
    |  3   | -wx  |
    |  4   | r--  |
    |  5   | r-x  |
    |  6   | rw-  |
    |  7   | rwx  |

    

## chown命令

> **修改**文件、文件夹的所属用户和用户组
>
> 注意：只适用于root用户

```shell
chown [-R] [用户][:][用户组] 文件或文件夹
```

- `-R`：对文件夹内的全部内容应用同样的操作
- `:`：表示分隔符











# 

# 实用操作



## 快捷键



### Ctrl+C

- 快捷键：强制停止

- 当输入内容有误时也可以使用，即重新输入



### Ctrl+D

- 退出账户的登录
- 退出某些特定程序的专属界面（Python解释器环境...）



### history

- 查看历史输入过的命令

- 使用`!`命令前缀，自动执行上一次匹配前缀的命令



### Ctrl+r

- 输入部分字符，匹配历史指令

- 按`Enter`直接执行匹配的命令
- 按左右箭头得到该指令不执行（无法切换匹配）



### 光标移动

- Ctrl+a：跳到命令开头
- Ctrl+e：跳到命令结尾
- Ctrl+⬅：向左跳一个单词
  - Ctrl+➡：向右跳一个单词



### Ctrl+l

- 清屏





## 软件



### yum命令

> 安装、卸载软件

- yum：RPM包软件管理器，用于自动化安装配置Linux软件，并可以自动解决依赖问题

- ```shell
  yum [-y] [install | remove | search] 软件名称
  ```

- `-y`：自动确认，无需手动确认安装或卸载过程

- install = 安装  remove = 卸载  search = 搜索

- 注意：

  - root权限或者sudo
  - 联网





### systemctrl

> 启动关闭软件

```shell
systemctl start | stop | status | enable | disable 服务名
```

- 参数说明：
  - enable：开启开机自启
  - disable：关闭开机自启
- 系统内置服务：
  - NetworkManager：主网络服务
  - network：：副网络服务
  - firewalld：防火墙服务
  - sshd：ssh服务（FinalSHell远程登录Linux使用的就是这个服务）





### ln

> link。软连接。快捷方式

```shell
ln -s from_obj to_obj
```







## 日期和时区



### date

```shell
date [-d] [+格式化字符串]
```

- 格式化字符串：（字符串防止空格解析为参数）

|      |             |      |                   |
| :--: | :---------: | :--: | :---------------: |
| `%Y` |     年      | `%y` | 年份后两位(00-99) |
| `%m` | 月份(01-12) | `%d` |     日(01-31)     |
| `%H` | 小时(00-23) | `%M` |    分钟(00-59)    |
| `%S` |  秒(00-60)  | `%s` |      时间戳       |

- `-d`：进行日期的计算：
  - 示例：`date -d "+1 day" "+%Y-%m-%d"` 表示后一天的日期

|        |      |        |      |
| :----: | :--: | :----: | :--: |
|  year  |  年  | month  |  月  |
|  day   |  天  |  hour  | 小时 |
| minute | 分钟 | second |  秒  |



### 修改时区

> root权限

```shell
rm -f /etc/localtime
sudo ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

- 先删除已有的时区信息（位于/etc/localtime）
- 再添加对应时区的软连接





### 自动校准时间

> 借助ntp程序

- 安装ntp：`yum -y install ntp` 
- 启动并设置开机自启：
  - `systemctl start ntpd` 
  - `systemctl enable ntpd` 
- 手动校准（root）：`ntpdate -u ntp.aliyun.com` 



- CentOS-8及其以上建议使用chrony包进行时间管理更好（可能自动安装过了）

- ```shell
  sudo yum install chrony  # 安装替代工具
  sudo systemctl start chronyd  # 启动服务
  sudo systemctl enable chronyd  # 设置开机自启
  ```





## 网络

> etc：Editable Text Configuration



### IP地址和主机名

- 查看ip地址：`ifconfig` （如果无法使用，可以安装：`yum -y install net-tools`）
- 特殊ip地址：
  - `127.0.0.1`：本机地址
  - `0.0.0.0`：可以用于本机。确定绑定关系。方形规则中表示所有IP均可访问
- 查看主机名：`hostname` 
- 修改主机名（root）：`hostnamectl set-hostname 主机名`





### 域名

- 域名解析文件（先本地解析再在线DNS服务器解析）：
  - windows：`C:\Windows\System32\drivers\hosts` 
  - linux：`/etc/hosts` 

- 修改配置内容即可指定域名的ip地址





### 固定IP

- 原因：
  - 每次重启设备都会动态获取IP地址。
  - Linux系统ip地址频繁更改会导致适配麻烦
  - 虚拟机IP地址和主机名的映射关系也需要更改
- 在VMware Workstation中配置固定IP：
  1. 在VMware Workstation中配置IP地址网关和网段（IP地址的范围）
     - <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250902192751096.png" alt="image-20250902192751096" style="zoom: 50%;" />
     - <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250902192907572.png" alt="image-20250902192907572" style="zoom:50%;" />
     - <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250902192958572.png" alt="image-20250902192958572" style="zoom:50%;" />
  2. 在Linux系统中手动修改配置文件，固定IP（root权限）（网卡文件信息不一定一样ens66）
     - ![image-20250902193124741](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250902193124741.png)
     - 执行：`systemctl restart NetworkManager` 重新启动网关（重启一样的）





### ping（无法ping）

> 网络请求

```shell
ping [-c num] ip|主机名
```

- `-c`：count。检查的次数，默认无限次数持续检查





### wget

> 下载

```shell
wget [-b] url
```

- `-b`：在后台下载。日志写入到当前工作目录的wget-log文件
- 通过tail指令可以监控后台下载进度：`tail -f wget-log` 





### curl

> 发送http请求。可用于：下载文件、获取信息等

```shell
curl [-O] url
```

- `-O`：用于下载文件





### 端口

- 公认端口：1~1023，通常用于一些系统内置或知名程序得预留使用，如SSH服务的22端口，HTTPS服务的443端口非特殊需要，不要占用这个范围的端口。
- 注册端口：1024~49151，通常可以随意使用，用于松散的绑定一些程序/服务。
- 动态端口：49152~65535，通常不会固定绑定程序，而是当程序对外进行网络链接时，用于临时使用。



#### nmap

> 查看端口的占用情况

- 使用yum指令安装nmap

```shell
nmap url
```





#### netstat

> 查看指定端口的占用情况

- 安装netstat：`yum -y install net-tools` 

```shell
netstat -anp | grep 端口号
```







### 进程管理



#### ps

```shell
ps [-e -f]
```

- `-e` ：显示出全部的进程
- `-f`：以完全格式化的形式展示信息（展示全部信息）
- 一般固定用法：`ps -ef` 

- 信息解读：

|       |                                              |
| :---: | -------------------------------------------- |
|  UID  | 进程所属的用户ID                             |
|  PID  | 进程的进程号ID                               |
| PPID  | 进程的父ID（启动此进程的其他进程）           |
|   C   | 此进程的CPU占用率（百分比）                  |
| STIME | 进程的启动时间                               |
|  TTY  | 启动此进程的终端序号。（？：表示非终端启动） |
| TIME  | 进程占用CPU的时间                            |
|  CMD  | 进程对应的名称或启动路径或启动命令           |



#### kill

> 关闭进程

```shell
kill [-9] 进程ID
```

- `-9`：强制关闭进程。不适用的话取决于进程自身的关闭机制
- 进程ID=PID





#### top

> 查看系统资源占用

```shell
top
```

- 每5s刷新
- 参数选项：
  - ![image-20250903142614814](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250903142614814.png)
- 信息解读：
  - ![image-20250903141624398](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250903141624398.png)
  - <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250903142119569.png" alt="image-20250903142119569" style="zoom:67%;" />
  - ![image-20250903142943247](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250903142943247.png)





#### df

> 查看硬盘的使用情况

```shell
df [-h]
```

- `-h`：更加人性化的单位显示



#### iostat

> 查看CPU、磁盘的相关信息

```shell
iostat [-x] [num1][num2]
```

- `-x`：显示更多信息
- `num1`：刷新间隔
- `num2`：刷新次数

- 信息解释：
  - ![image-20250904102859363](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250904102859363.png)





#### sar

> 网络状态监控

```shell
sar -n DEV num1 num2
```

- `-n`：查看网络，DEV表示查看网络接口
- num12同上
- 信息解读：
  - <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20250904103157523.png" alt="image-20250904103157523" style="zoom:50%;" />







### 环境变量



#### env

> 查看环境变量。KeyValue格式



#### path配置

```shell
env | grep path
```

- 不同的目录用冒号`:`连接。同Windows的搜索环境




#### \$

> 取变量值。环境变量。

```shell
echo $PATH
echo "hello ${PATH}"
```





#### export

> 自行设置环境变量

```shell
export variable=value
```

- 永久生效
  - 针对当前用户生效，配置在当前用户的：`~/bashrc` 
  - 针对所有用户生效，配置在系统的：`/etc/profile` 
  - 并通过语法：`source 配置文件`，进行立刻生效，或重新登录生效。





#### 配置环境变量

1. root权限下的`/etc/profile`进行配置
2. 执行的指令文件需要有可运行的权限（755权限）
3. 配置的环境需要在原有的环境基础上进行添加，而不是覆盖

```shell
export PATH=$PATH:环境路径
chmod 755 file
```





## 文件操作



### 本地上传和下载文件

> 仅对finalshell工具有效

- 手动
  - 通过使用软件finalshell连接到linux服务器之后，可以直接通过下方的文件目录功能可视化上传和下载

- 代码

  - 使用lrzsz库进行控制台代码操作

  - 上传：

    - ```shell
      rz
      ```

    - 在finalshell中执行之后会给出弹窗，虚拟机里面无法弹窗，会卡住窗口

  - 下载：

    - ```shell
      sz 文件
      ```

    - 自动保存在桌面，并创建一个文件夹进行保存。fsdownload



- 理解指令：
  - 包lrzsz是基于Zmodem协议的文件传输工具。
  - `rz`：表示recieve Zmodem
  - `sz`：表示send Zmodem





### 压缩和解压

- Linux常用的压缩格式：`zip`、`tar`、`gzip` 



#### tar

> 针对压缩格式 .tar、.gz

- 适用的压缩格式：

  - `.tar`：tarball，归档文件，仅仅封装文件，压缩效果微小

  - `.gz`：也常见为`.tar.gz`，gzip格式压缩文件，极大的减少压缩后的体积

```shell
tar [-c -v -x -f -z -C] arg1 arg2 ... arguN
```

- `-c`：压缩模式
- `-v`：view。显示进度
- `-x`：解压模式
- `-f`：file。指定文件。该参数必须放在最后面
- `-z`：是否使用gzip模式。默认是tarball模式
- `-C`：选择解压的路径。（解压模式）



- 常见的压缩组合：

  - `cvf`：tar压缩文件

  - ```shell
    tar -cvf test.tar 1.txt 2.txt 3.txt
    ```

  - `zcvf`：gzip压缩文件

  - ```shell
    tar -zcvf test.tar 1.txt 2.txt 3.txt
    ```

  - 注意：

    - `-z`：一般放在首位
    - `-f`：一般放在选项最后一位

- 常见的解压组合：

  - ```shell
    tar -xvf test.tar
    ```

  - ```shell
    tar -xvf test.tar -C /home/test
    ```

  - ```shell
    tar -zxvf test.tar -C /home/test
    ```

  - 注意：

    - `-C`：单独使用，区分参数

    - 解压的时候，不会先创建一个文件夹，只能自己提前创建文件夹






#### zip

> 压缩zip

```shell
zip [-r] arg1 arg2 ... argN
```

- `-r`：当压缩的文件里面包含文件夹的时候，需要使用



#### upzip

> 解压zip

```shell
unzip [-d] 参数
```

- `-d`：指定要解压的位置

- ```shell
  unzip test.zip -d /home/test
  ```





# 实战



## MySQL数据库管理系统安装部署



1. 配置yum仓库

   ```shell
   # 更新密钥
   rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
   
   # 安装Mysql8.x版本 yum库
   rpm -Uvh https://dev.mysql.com/get/mysql80-community-release-el7-2.noarch.rpm
   ```

2. 使用yum安装MySQL

   ```shell
   yum -y install mysql-community-server
   ```

3. 安装完成后，启动MySQL并配置开机自启动

   ```shell
   systemctl start mysqld
   systemctl enable mysqld
   ```

4. 检查MySQL的运行状态

   ```shell
   systemctl status mysqld
   ```

   

- 修改密码

  1. 获取MySQL的初始密码

     ```shell
     grep 'temporary password' /var/log/mysqld.log
     ```

  2. 登录MySQL数据库系统

     ```shell
     mysql -uroot -p
     ```

  3. 修改root密码

     ```sql
     ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_password BY '密码';
     # 密码要求：大于8位；大小写字母；特殊符号
     # 删去 WITH mysql_password
     ```

  4. 设置简单密码

     ```sql
     set global validate_password.policy=0; # 安全等级低
     set global validate_password.length=4; # 密码长度最低4位
     ```





- 远程登录

  ```sql
  # 远程登录的密码需要另外设置。“%”表示允许任意的ip远程登录。多个ip需要多次执行
  create user 'root'@'%' IDENTIFIED WITH mysql_native_password BY '密码';
  
  # 后续修改密码用此命令
  ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '密码';
  ```

  



- 远程连接

  - 开放防火墙允许3306端口远程访问

    ```shell
    # 开放3306端口（永久生效）
    sudo firewall-cmd --add-port=3306/tcp --permanent
    
    # 重新加载防火墙规则
    sudo firewall-cmd --reload
    
    # 验证端口是否开放
    sudo firewall-cmd --list-ports | grep 3306
    ```

  - 检查 MySQL 配置是否绑定本地地址（关键！）

    - 编辑 MySQL 配置文件，确保没有绑定到 `127.0.0.1`：

    ```shell
    sudo vi /etc/my.cnf  # 或 /etc/my.cnf.d/mysql-server.cnf
    ```

    - 查找 `bind-address` 配置，若存在则注释掉（加 `#`），或改为 `0.0.0.0`（允许所有 IP 访问）：

    ```shell
    # bind-address = 0.0.0.0  # 注释掉这行
    ```

    - 保存后重启 MySQL：

    ```shell
    sudo systemctl restart mysqld
    ```

  - 远程连接：

    ```shell
    mysql -h 虚拟机IP -P 3306 -u root -p
    ```

  - 授予权限：

    ```sql
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
    ```

    





































































# 解决下载仓库失效问题

```shell
# 备份原有仓库配置
mkdir /etc/yum.repos.d/backup
mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup/

# 下载并替换为Vault仓库配置
curl -o /etc/yum.repos.d/CentOS-Base.repo https://vault.centos.org/centos/8.5.2111/BaseOS/x86_64/os/Packages/centos-linux-repos-8-3.el8.noarch.rpm
rpm2cpio /etc/yum.repos.d/CentOS-Base.repo | cpio -idv ./etc/yum.repos.d/CentOS-Linux-*
mv ./etc/yum.repos.d/CentOS-Linux-* /etc/yum.repos.d/
rm -f /etc/yum.repos.d/CentOS-Base.repo  # 清理临时文件

# 编辑仓库配置，将所有仓库地址替换为Vault地址
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-*.repo
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*.repo

# 清除yum缓存并更新
yum clean all
yum makecache
```























































