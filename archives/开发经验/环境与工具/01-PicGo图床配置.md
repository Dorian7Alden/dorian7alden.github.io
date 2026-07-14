---
create-time: 未知
update-time: 2026-07-13
---



# PicGo Core 使用教程（Windows 版）

PicGo Core 是 PicGo 的命令行版本，无需图形界面，可以直接在终端中完成图片上传，并将返回的链接打印到标准输出。它非常适合集成到 Typora、VS Code 等编辑器中，实现一键上传图片到 Gitee、GitHub 等图床。

本教程以 Gitee 图床为例，完整覆盖 PicGo Core 的安装、配置与使用。

---

## 第 1 步：安装 Node.js 运行环境

PicGo Core 依赖 Node.js，请先安装 Node.js 的 LTS 长期支持版。

- 官网下载：https://nodejs.org/
- 安装过程中**务必勾选 “Add to PATH”**，将 Node.js 加入系统环境变量。
- 安装完成后，打开**全新的**命令行窗口，输入以下命令验证：

```cmd
node -v
npm -v
```

若能正常显示版本号，说明 Node.js 环境已就绪。

---

## 第 2 步：全局安装 PicGo Core

在命令行中执行：

```cmd
npm install picgo -g
```

安装完成后，检查版本：

```cmd
picgo -v
```

显示版本号即表示 PicGo Core 安装成功。

---

## 第 3 步：安装对应的图床插件

以 Gitee 为例，安装上传插件：

```cmd
picgo install picgo-plugin-gitee-uploader
```

如果是 GitHub 图床，则安装 `picgo-plugin-github-uploader`，其他图床同理。安装后 PicGo Core 才能识别对应的配置项。

---

## 第 4 步：配置图床信息

执行以下命令打开 PicGo Core 的配置文件：

```cmd
picgo config edit
```

在打开的 JSON 文件中，填入你的 Gitee 图床信息。下面是配置模板，请替换为实际值：

```json
{
  "picBed": {
    "uploader": "gitee",
    "gitee": {
      "repo": "你的用户名/仓库名",
      "token": "你的Gitee私人令牌",
      "path": "typora/",
      "branch": "master"
    }
  },
  "picgoPlugins": {
    "picgo-plugin-gitee-uploader": true
  }
}
```

> **字段说明**  
> - `repo`：格式为 `用户名/仓库`，不要带 `https://gitee.com/` 前缀。  
> - `token`：Gitee 私人令牌，需具备仓库的读写权限。  
> - `path`：图片在仓库中的存储路径，可按需修改。  
> - `branch`：仓库分支，一般用 `master`。

保存并关闭文件，配置即时生效。

---

## 第 5 步：终端测试上传

在命令行中直接上传一张本地图片，验证整个链路是否打通：

```cmd
picgo upload "C:\Users\你的用户名\Desktop\example.png"
```

请将路径替换为你电脑中真实存在的一张图片。

如果一切正常，终端会直接输出一行图片链接，类似：

```
https://gitee.com/xxx/images/raw/master/typora/example.png
```

这就意味着 PicGo Core 已能独立工作，并把结果输出到标准输出（这也是编辑器能获取链接的关键）。

---

## 第 6 步：集成到 Typora（或其他编辑器）

PicGo Core 最常见的应用场景是配合 Markdown 编辑器实现自动上传。这里以 Typora 为例：

1. 打开 Typora → 文件 → 偏好设置 → **图像**。
2. 在“插入图片时…”选择需要的操作（如“上传图片”）。
3. “上传服务设定”中，**Image Uploader** 选择 **“Custom Command”**。
4. “命令”输入框里填入：

```cmd
picgo upload
```

5. 点击「测试上传」按钮，选择一张图片，若弹出成功提示并显示链接，即表示集成完成。

之后在 Typora 里粘贴或拖入图片，PicGo Core 会自动上传并将图片链接回填到文档中。

> **其他编辑器**  
> 只要支持自定义命令上传并读取命令的标准输出，同样可以使用 `picgo upload` 进行集成。

---

## 常用管理命令

- 查看当前配置：`picgo config show`
- 安装其他插件：`picgo install <plugin-name>`
- 卸载插件：`picgo uninstall <plugin-name>`
- 查看已安装插件：`picgo plugin list`

如果在使用中遇到问题，首先检查 Node.js 环境是否正确，以及配置文件中的 `repo`、`token` 是否填写无误。







# PicGo Core 使用教程（Ubuntu 版）

PicGo Core 是 PicGo 的命令行版本，无需图形界面，可以直接在终端中完成图片上传，并将返回的链接打印到标准输出。它非常适合集成到 Typora、VS Code 等编辑器中，实现一键上传图片到 Gitee、GitHub 等图床。

本教程以 **Gitee** 图床为例，完整覆盖 PicGo Core 在 **Ubuntu** 系统下的安装、配置与使用。文中所有命令均在 Ubuntu 22.04/24.04 及衍生发行版中验证通过。

---

## 第 1 步：安装 Node.js 运行环境

PicGo Core 依赖 Node.js。在 Ubuntu 下推荐使用 **nvm**（Node Version Manager）安装，以便管理多个版本且无需 `sudo` 权限。

**方法一（推荐）：使用 nvm**

1. 安装 nvm（若未安装）：
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
   ```
   安装完成后，重新打开终端或执行 `source ~/.bashrc`（若使用 zsh 则 `source ~/.zshrc`）使 nvm 生效。

2. 安装 Node.js LTS 版本（例如 20.x）：
   ```bash
   nvm install --lts
   nvm use --lts
   ```

3. 验证安装：
   ```bash
   node -v
   npm -v
   ```
   若能正常显示版本号，说明 Node.js 环境已就绪，并且 `node` 和 `npm` 命令已自动加入 PATH。

**方法二：使用 Ubuntu 官方源**

也可使用 apt 安装，但版本可能较旧，不推荐：
```bash
sudo apt update
sudo apt install nodejs npm
```
安装后同样用 `node -v` 和 `npm -v` 验证。

---

## 第 2 步：全局安装 PicGo Core

在终端中执行：

```bash
npm install picgo -g
```

安装完成后，检查版本：

```bash
picgo -v
```

显示版本号即表示 PicGo Core 安装成功。

> **注意**：若使用 nvm，`picgo` 命令会自动安装到当前 Node 版本的 bin 目录下，且已在 PATH 中。若使用 apt 安装的 Node.js，可能需要将 `/usr/local/bin` 加入 PATH（通常已加入）。

---

## 第 3 步：安装对应的图床插件

以 Gitee 为例，安装上传插件：

```bash
picgo install picgo-plugin-gitee-uploader
```

如果是 GitHub 图床，则安装 `picgo-plugin-github-uploader`，其他图床同理。安装后 PicGo Core 才能识别对应的配置项。

---

## 第 4 步：配置图床信息

PicGo Core 的配置文件位于 `~/.picgo/config.json`。你可以通过以下两种方式编辑：

- 尝试使用命令（可能因系统或版本原因无效）：
  ```bash
  picgo config edit
  ```
  该命令会调用系统默认编辑器打开配置文件。**但部分 Ubuntu 系统下此命令可能无法正常打开编辑器**，此时请采用手动编辑方式。

- **推荐方式：手动编辑配置文件**：
  ```bash
  nano ~/.picgo/config.json
  ```
  或使用你喜欢的编辑器（如 `vim`、`gedit` 等）。

在打开的 JSON 文件中，填入你的 Gitee 图床信息。下面是配置模板，请替换为实际值：

```json
{
  "picBed": {
    "uploader": "gitee",
    "gitee": {
      "repo": "你的用户名/仓库名",
      "token": "你的Gitee私人令牌",
      "path": "typora/",
      "branch": "master"
    }
  },
  "picgoPlugins": {
    "picgo-plugin-gitee-uploader": true
  }
}
```

> **字段说明**  
>
> - `repo`：格式为 `用户名/仓库`，不要带 `https://gitee.com/` 前缀。  
> - `token`：Gitee 私人令牌，需具备仓库的读写权限。  
> - `path`：图片在仓库中的存储路径，可按需修改。  
> - `branch`：仓库分支，一般用 `master`。

保存并关闭文件，配置即时生效。  
如需查看当前生效的配置，可执行 `picgo config show`。

---

## 第 5 步：终端测试上传

在终端中直接上传一张本地图片，验证整个链路是否打通：

```bash
picgo upload ~/Pictures/example.png
```

请将路径替换为你电脑中真实存在的一张图片（支持绝对路径或相对路径）。

如果一切正常，终端会直接输出一行图片链接，类似：

```
https://gitee.com/xxx/images/raw/master/typora/example.png
```

这就意味着 PicGo Core 已能独立工作，并把结果输出到标准输出（这也是编辑器能获取链接的关键）。

---

## 第 6 步：集成到 Typora（或其他编辑器）

PicGo Core 最常见的应用场景是配合 Markdown 编辑器实现自动上传。这里以 Typora 为例：

1. 打开 Typora → 文件 → 偏好设置 → **图像**。
2. 在“插入图片时…”选择需要的操作（如“上传图片”）。
3. “上传服务设定”中，**Image Uploader** 选择 **“Custom Command”**。
4. “命令”输入框里填入：
   ```
   picgo upload
   ```
   但若 Typora 无法找到 `picgo` 命令（因其启动时可能不加载 shell 环境变量），**推荐使用包装脚本**，例如创建 `~/bin/picgo-typora` 文件，内容如下：
   ```bash
   #!/bin/bash
   export PATH="/home/你的用户名/.nvm/versions/node/v20.11.0/bin:$PATH"
   exec /home/你的用户名/.nvm/versions/node/v20.11.0/bin/picgo "$@"
   ```
   赋予执行权限：
   ```bash
   chmod +x ~/bin/picgo-typora
   ```
   然后在 Typora 的“命令”框中填入：
   ```
   /home/你的用户名/bin/picgo-typora upload
   ```
   这样可以确保 Typora 调用正确的 Node.js 和 PicGo 环境。

5. 点击「测试上传」按钮，选择一张图片，若弹出成功提示并显示链接，即表示集成完成。

之后在 Typora 里粘贴或拖入图片，PicGo Core 会自动上传并将图片链接回填到文档中。

> **其他编辑器**  
> 只要支持自定义命令上传并读取命令的标准输出，同样可以使用 `picgo upload` 进行集成，但需注意环境变量问题，建议使用包装脚本。

---

## 常用管理命令

- 查看当前配置：`picgo config show`
- 安装其他插件：`picgo install <plugin-name>`
- 卸载插件：`picgo uninstall <plugin-name>`
- 查看已安装插件：`picgo plugin list`

---

## 常见问题（Ubuntu 环境）

**Q：执行 `picgo` 提示 `command not found`**  
A：确保 Node.js 的 bin 目录在 PATH 中。若使用 nvm，请确认 `nvm use` 已切换到正确的版本，并将 `$(nvm which current)` 加入 PATH（通常 nvm 已自动处理）。若使用 apt 安装的 Node.js，可执行 `export PATH=/usr/local/bin:$PATH` 并写入 `~/.bashrc`。

**Q：Typora 中调用 `picgo upload` 失败，但终端可以**  
A：Typora 作为桌面应用，可能无法继承终端的 PATH 环境变量。解决方法：  
- 使用**绝对路径**（如 `/home/用户名/.nvm/versions/node/v20.11.0/bin/picgo upload`）。  
- 或创建包装脚本（参考第 6 步中的示例），并将 Typora 的命令指向该脚本。

**Q：上传时报 `文件名已存在`（400 错误）**  
A：Gitee 不允许同名文件覆盖。解决办法：在配置文件的 `path` 字段中加入动态变量，例如：
```json
"path": "typora/{year}/{month}/{day}/{filename}_{timestamp}"
```
或启用 PicGo 的重命名功能（参见 PicGo 官方文档）。

**Q：`picgo config edit` 无法打开编辑器**  
A：这是常见问题，无需惊慌。请直接使用终端文本编辑器手动编辑 `~/.picgo/config.json` 文件，如 `nano ~/.picgo/config.json`。

---

如果在使用中遇到其他问题，请首先检查 Node.js 环境是否正确，以及配置文件中的 `repo`、`token` 是否填写无误。也可通过 `picgo config show` 查看当前生效的配置。