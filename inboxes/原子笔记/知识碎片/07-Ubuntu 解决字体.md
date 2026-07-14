# Ubuntu 系统字体配置经验卡片

## 📌 配置目标

在 Ubuntu 系统中实现以下字体效果：

| 使用场景                           | 英文字体                  | 中文字体                        |
| ---------------------------------- | ------------------------- | ------------------------------- |
| **系统界面 / 终端 / 代码编辑器**   | `JetBrainsMono Nerd Font` | `Noto Sans Mono CJK SC`（后备） |
| **Markdown Preview Enhanced 预览** | `JetBrainsMono Nerd Font` | `Noto Sans Mono CJK SC`（后备） |

核心思路：**英文和代码用 JetBrains Mono，中文自动回退到 Noto Sans Mono CJK SC**。

------

## 📦 前置准备：安装所需字体

```bash
# 安装 Noto CJK 中文字体
sudo apt install fonts-noto-cjk

# 安装 JetBrainsMono Nerd Font（从官方 GitHub 下载）
# 访问: https://github.com/ryanoasis/nerd-fonts/releases
# 下载 JetBrainsMono.zip，解压后双击 .ttf 文件点击"安装字体"
```

确认字体已安装：

```bash
fc-list | grep "JetBrainsMono"
fc-list | grep "Noto Sans Mono CJK SC"
```

------

## ⚙️ 第一部分：系统字体配置（后备字体机制）

### 配置文件位置

```
~/.config/fontconfig/fonts.conf
```

### 完整配置内容

```xml
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <!-- 为 JetBrainsMono Nerd Font 设置后备字体 -->
  <alias>
    <family>JetBrainsMono Nerd Font</family>
    <prefer>
      <family>JetBrainsMono Nerd Font</family>
      <family>Noto Sans Mono CJK SC</family>
    </prefer>
  </alias>
  <!-- 为等宽字体类别设置首选字体 -->
  <alias>
    <family>monospace</family>
    <prefer>
      <family>JetBrainsMono Nerd Font</family>
      <family>Noto Sans Mono CJK SC</family>
    </prefer>
  </alias>
</fontconfig>
```

### 使配置生效

```bash
fc-cache -fv
```

### 验证配置是否生效

```bash
# 检查字体优先级链
fc-match -s "JetBrainsMono Nerd Font" | head -10
```

**预期输出**（关键行）：

```plain
JetBrainsMonoNerdFont-Regular.ttf: "JetBrainsMono Nerd Font" "Regular"
NotoSansCJK-Regular.ttc: "Noto Sans Mono CJK SC" "Regular"
```

------

## 📝 第二部分：Markdown Preview Enhanced 插件字体配置

由于 VS Code 的 Markdown 预览基于 Chromium 内核，**不继承系统字体配置**，需单独设置。

### 配置步骤

1. **打开命令面板**：`F1` 或 `Ctrl + Shift + P`
2. **执行命令**：输入并选择 `Markdown Preview Enhanced: Customize CSS (Global)`
3. **编辑** `style.less` **文件**，添加以下内容：

```css
/* Markdown Preview Enhanced 预览区字体 */
.markdown-preview.markdown-preview {
    font-family: 'JetBrainsMono Nerd Font', 'Noto Sans Mono CJK SC', sans-serif;
}
```

1. **保存文件**，重新打开 Markdown 预览窗口即可生效。

### 字体顺序说明

| 顺序 | 字体                      | 作用                   |
| ---- | ------------------------- | ---------------------- |
| 1    | `JetBrainsMono Nerd Font` | 英文/代码/数字优先使用 |
| 2    | `Noto Sans Mono CJK SC`   | 中文作为后备           |
| 3    | `sans-serif`              | 系统兜底字体           |

------

## 🔍 验证方法

### 系统终端验证

```bash
echo "你好世界 Hello World 123 !@#"
```

观察中英文是否分别使用不同字体渲染。

### VS Code Markdown 预览验证

创建一个 `test.md` 文件，内容为：

```markdown
# 你好世界 Hello World

这是一段中文 mixed with English and code `const foo = 123;`
```

预览窗口中，中英文应呈现不同的字形风格。

------

## 📂 配置文件速查

| 配置对象                  | 配置文件路径                                    | 说明                                 |
| ------------------------- | ----------------------------------------------- | ------------------------------------ |
| 系统字体后备              | `~/.config/fontconfig/fonts.conf`               | 用户级 fontconfig 配置               |
| Markdown Preview Enhanced | 命令面板 → `Customize CSS (Global)`             | 编辑 `style.less`                    |
| VS Code 终端字体          | VS Code 设置 → `terminal.integrated.fontFamily` | 可选：设为 `JetBrainsMono Nerd Font` |

------

## ⚠️ 常见问题排查

| 问题现象               | 可能原因           | 解决方案                          |
| ---------------------- | ------------------ | --------------------------------- |
| 配置不生效             | 字体名称写错       | 用 `fc-list` 确认准确名称         |
| 中文显示为方块         | 未安装中文字体     | `sudo apt install fonts-noto-cjk` |
| Markdown 预览字体未变  | 未重启预览窗口     | 关闭后重新打开预览                |
| `fc-match` 未显示 Noto | 配置文件有语法错误 | 检查 XML 标签是否闭合             |

------

## 💡 延伸知识

- `fontconfig` 的 `<prefer>` 列表按**从上到下**的优先级匹配，遇到包含当前字符的字体即停止。
- Markdown Preview Enhanced 的 `style.less` 会覆盖插件默认样式，修改后**实时生效**，无需重启 VS Code。
- 如果需要在其他应用（如 WPS、Chrome）中应用相同字体，通常需要在该应用的设置中单独配置，系统级后备字体不一定会自动继承。