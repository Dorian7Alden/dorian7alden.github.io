# PicGo Core 使用教程

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