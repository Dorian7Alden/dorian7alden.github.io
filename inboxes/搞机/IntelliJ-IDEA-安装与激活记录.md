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





IntelliJ 激活码：

```
4ZM1APWA28-eyJsaWNlbnNlSWQiOiI0Wk0xQVBXQTI4IiwibGljZW5zZWVOYW1lIjoiVGVzdCBvbmx5IiwiYXNzaWduZWVOYW1lIjoiVGVzdCBvbmx5IiwiYXNzaWduZWVFbWFpbCI6IiIsImxpY2Vuc2VSZXN0cmljdGlvbiI6IiIsImNoZWNrQ29uY3VycmVudFVzZSI6ZmFsc2UsInByb2R1Y3RzIjpbeyJjb2RlIjoiSUkiLCJmYWxsYmFja0RhdGUiOiIyMDMwLTEyLTMxIiwicGFpZFVwVG8iOiIyMDMwLTEyLTMxIn0seyJjb2RlIjoiUENXTVAiLCJmYWxsYmFja0RhdGUiOiIyMDMwLTEyLTMxIiwicGFpZFVwVG8iOiIyMDMwLTEyLTMxIn0seyJjb2RlIjoiUFNJIiwiZmFsbGJhY2tEYXRlIjoiMjAzMC0xMi0zMSIsInBhaWRVcFRvIjoiMjAzMC0xMi0zMSJ9XSwibWV0YWRhdGEiOiIwMTIwMjMwMTAyUFBBQTAxMzAwOSIsImhhc2giOiI0MTQ3Mjk2MS8wOjE1NjM2MDk0NTEiLCJncmFjZVBlcmlvZERheXMiOjcsImF1dG9Qcm9sb25nYXRlZCI6dHJ1ZSwiaXNBdXRvUHJvbG9uZ2F0ZWQiOnRydWV9-mBQVrFiAN9kuf+W7CgmJQpPmY9MbCN2oZJSLwX+pGdxIEei7txG7PUAxyXs2Te7BGkCebI7uP7ZLRCyVl9ksqOJizZSbfFfe1Abo9NpXUFY9fYLYBRpLLA2hD18w/pcM8XyhiaN8kJ07vgcvR9I1RhzamdSpbp9EXiganbSAremve4X7knYRyl71DWu9Ac4L3yVBg601+7/ktv+mdwnLWDPjNULlgtjJWIzPxlpt0Fskks0ThPTwVCJklaka9d+9fVF0TuUZo14CkY1kXpTncgT7tpLdIJTiwTuZwkfgvT67k5POhZRGNSG2V0CHN65+OY5cLNCtrijtE5NCgNYx+HWi1EaXWqxvHYkQ2ElXrAsbqIoetXSyXtt4JRMpHg4JL3cHr31IMVkPZ4xNsuQoeeXGinK+AOPn3zE3lwhD9PsbJFoU3eEg/8v7OiBddtwwiAZrUPzY7PL0zSSIFlA8P9q1LoRpZ+fYIMmnmkgV/o+y5K2oBV0rG4RqFKKa6UxfBbQOINfqeHFHP42VABLIYTWsoSvhUIHDc9VHdme0j+O6ctey5YqFAdf9e/jkwRpiW0s33D+FTFDoXw3tTt55bs+dp1KEQBaUlIZK+ltNP3TVBOx18aV0C7PqO7TJM66bcMN8Pkp0yx5uOAsInYMI4+LNkHNqbQhLa4hDq9Iz+g4=-MIIEtTCCAp2gAwIBAgIUDyuccmylba71lZQAQic5TJiAhwwwDQYJKoZIhvcNAQELBQAwGDEWMBQGA1UEAwwNSmV0UHJvZmlsZSBDQTAeFw0yMzA5MjkxNDA2MTJaFw0zMzA5MjcxNDA2MTJaMBExDzANBgNVBAMMBk5vdmljZTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBALenqcGP2ZxGkYqmKA9c4Hzf8+YD1smvmOxKjd+bmTLrutM/hXv1cj1rW3/lqyDtdDk7K6W8/TDq1CRrEt+Do6l30DxhAiC34aH8DmGwgq77xEoLimvH5LpePxflF+tbB1RZtFgFDOIYLdSQaKFH2JDgVKxhLiV3S6jniPhkCtWWrTs+E6vq4N15Bm3NnM5AJILqjtUbOjNfaxVq6RrOoTc0R3Fqqo6yvxo/+JYa2UnHIC+r2dbKuDLMUrtgnydEUdJNX0zH9FtcdELvr48uc9mY038TWUsZUK1pnQbxA2bPyA4qnYJ9IvUgO6LtLXvGFm137YQMS1N41AHDBOrwoNI8UoDX+qI3rM96biFOFvn7Edky7rByzybt3H+zxdojfjvpL1E0NO98BT9zfufHAaAxZtlmDOu5LDJe3CGurnyRMRExbtc+Qjl1mUh6tG4lakAwdsoxry0GdG72yaYyb9it53kaFks/T/s7Z7bRJzVFzQDV1Y4bzUtk43vKm2vztBVlQkBkZY5f2Jbe5Ig3b8swQzBnOT0mrL5SPUhwmQ6IxkEWztj55OEujBMmRr92oESuq9ZYMaeLidKWVR3/++HA8BRZaRGEKtSHZCbFEFdihDxxJv9Xh6NuT/ewJ6HYp+0NQpFnUnJ72n8wV+tudpam7aKcdzVmz7cNwOhG2Ls7AgMBAAEwDQYJKoZIhvcNAQELBQADggIBAIdeaQfKni7tXtcywC3zJvGzaaj242pSWB1y40HW8jub0uHjTLsBPX27iA/5rb+rNXtUWX/f2K+DU4IgaIiiHhkDrMsw7pivazqwA9h7/uA0A5nepmTYf/HY4W6P2stbeqInNsFRZXS7Jg4Q5LgEtHKo/H8USjtVw9apmE3BCElkXRuelXMsSllpR/JEVv/8NPLmnHSY02q4KMVW2ozXtaAxSYQmZswyP1YnBcnRukoI4igobpcKQXwGoQCIUlec8LbFXYM9V2eNCwgABqd4r67m7QJq31Y/1TJysQdMH+hoPFy9rqNCxSq3ptpuzcYAk6qVf58PrrYH/6bHwiYPAayvvdzNPOhM9OCwomfcazhK3y7HyS8aBLntTQYFf7vYzZxPMDybYTvJM+ClCNnVD7Q9fttIJ6eMXFsXb8YK1uGNjQW8Y4WHk1MCHuD9ZumWu/CtAhBn6tllTQWwNMaPOQvKf1kr1Kt5etrONY+B6O+Oi75SZbDuGz7PIF9nMPy4WB/8XgKdVFtKJ7/zLIPHgY8IKgbx/VTz6uBhYo8wOf3xzzweMnn06UcfV3JGNvtMuV4vlkZNNxXeifsgzHugCvJX0nybhfBhfIqVyfK6t0eKJqrvp54XFEtJGR+lf3pBfTdcOI6QFEPKGZKoQz8Ck+BC/WBDtbjc/uYKczZ8DKZu
```

