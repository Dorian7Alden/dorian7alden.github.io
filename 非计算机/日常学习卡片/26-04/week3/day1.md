



这是因为 **Git Bash（本质是 MinTTY 终端）** 在输出包含**非 ASCII 字符**（如中文、特殊 Unicode 字符）的文件名时，默认使用了 **UTF-8 的 URL 编码（Percent-Encoding）** 方式进行转义显示。

解决方案：修改全局配置。打开 Git Bash，执行以下命令，让 Git 在输出时不进行路径编码转义：

```bash
git config --global core.quotepath false
```

这个问题是 Windows 终端环境与 Git 原生 UTF-8 编码之间的兼容问题。现代版本的 Git For Windows 已默认包含 UTF-8 支持，只要正确配置了环境变量和 `core.quotepath`，就能完美解决中文显示异常的问题。

![image-20260413154817912](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260413154817912.png)