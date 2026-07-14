# IntelliJ IDEA 2026.1.3 安装与激活记录 (Ubuntu)

## 环境信息

- **操作系统:** Ubuntu Linux
- **Java 版本:** OpenJDK 21.0.11
- **IntelliJ 版本:** IDEA Ultimate 2026.1.3 (Build 261.25134.95)

---

## 一、安装

### 1.1 解压即用

从 JetBrains 官网下载 `ideaIU-2026.1.3.tar.gz`，解压后得到 `idea-IU-261.25134.95/` 目录。

### 1.2 移动到 /opt

```bash
sudo mv idea-IU-261.25134.95 /opt/
```

### 1.3 创建 CLI 启动命令

```bash
sudo ln -sf /opt/idea-IU-261.25134.95/bin/idea.sh /usr/local/bin/idea
```

此后在终端直接输入 `idea` 即可启动 IntelliJ。

### 1.4 创建桌面入口

首次启动后，在 IntelliJ 菜单栏点击 **Tools → Create Desktop Entry**，即可在系统应用菜单中找到 IntelliJ。

---

## 二、配置目录

IntelliJ 首次启动后会在以下位置生成配置：

```
~/.config/JetBrains/IntelliJIdea2026.1/
```

其中 `idea64.vmoptions` 是自定义 VM 选项文件，通过 IntelliJ 菜单 **Help → Edit Custom VM Options** 编辑。

---

## 三、激活

### 3.1 激活原理

使用开源项目 [ja-netfilter](https://gitee.com/ja-netfilter/ja-netfilter)（纯 Java 实现，跨平台），通过 JVM `-javaagent` 机制在运行时拦截许可证校验。

### 3.2 文件结构

激活所需文件部署在 `~/.script/intellij-activate/` 下：

```
~/.script/intellij-activate/
├── ja-netfilter.jar          # 核心 Java Agent
├── config/                   # 配置文件（8 个 .conf）
│   ├── dns.conf              # DNS 拦截
│   ├── env.conf              # 环境变量覆盖
│   ├── MethodResultModify.conf
│   ├── native.conf
│   ├── power.conf            # RSA 签名注入（核心）
│   ├── privacy.conf          # 反检测隐藏
│   ├── url.conf              # URL 拦截
│   └── xbase64.conf          # 字符串解码
└── plugins/                  # 插件 JAR（10 个）
    ├── dns.jar
    ├── env.jar
    ├── env-v1.0.2.jar
    ├── hideme.jar
    ├── method-result-modify.jar
    ├── native.jar
    ├── power.jar             # RSA 签名插件（核心）
    ├── privacy.jar
    ├── url.jar
    └── xbase64.jar
```

### 3.3 VM Options 配置

编辑 `~/.config/JetBrains/IntelliJIdea2026.1/idea64.vmoptions`，添加以下内容：

```properties
--add-opens=java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED
--add-opens=java.base/jdk.internal.org.objectweb.asm.tree=ALL-UNNAMED
-javaagent:/home/dorian/.script/intellij-activate/ja-netfilter.jar
```

### 3.4 应用激活码

1. 完全关闭并重启 IntelliJ IDEA
2. 进入 **Help → Manage Subscriptions...**
3. 选择 **Activation Code**
4. 粘贴激活码（以 `4ZM1APWA28-eyJ...` 开头的一长串 Base64 编码文本）
5. 点击 Activate

激活成功后显示 Licensed to "Test only"，有效期至 2030-12-31。

---

## 四、Linux vs Windows 差异说明

ja-netfilter 是纯 Java 项目，无平台依赖：

| 项目 | Windows | Ubuntu | 是否需适配 |
|------|---------|--------|-----------|
| VM options 文件 | `%APPDATA%\...` | `~/.config/...` | IDE 自动处理 |
| `-javaagent` 路径 | `C:\...\ja-netfilter.jar` | `/home/.../ja-netfilter.jar` | 仅路径格式 |
| `--add-opens` 参数 | 相同 | 相同 | 无需适配 |
| 激活码粘贴 | 相同 | 相同 | 无需适配 |
| config/plugins 相对路径 | 相同 | 相同 | 无需适配 |

**关键注意事项**: `config/` 和 `plugins/` 目录必须与 `ja-netfilter.jar` 放在同一目录下，agent 通过相对路径加载它们。

---

## 五、日常使用

- **启动:** 终端输入 `idea`，或通过系统应用菜单搜索 IntelliJ
- **更新激活文件:** 定期从 idea-set 仓库拉取最新的 `ja-netfilter.jar`、`config/`、`plugins/`，覆盖 `~/.script/` 下的对应文件，重启 IDE 即可
- **更换激活码:** 进入 Help → Manage Subscriptions → Remove License，然后重新粘贴新激活码
