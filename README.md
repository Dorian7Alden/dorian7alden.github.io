# Dorian's Blog

Author: Dorian Alden Dai

Time: 2026-05-06 03:57

## 简介
这是 Dorian Alden Dai 的个人技术博客项目。项目基于 **VitePress** 构建，旨在将外部的个人笔记转换为系统化的博客站点。

## 项目机制

本项目的一个核心特点是其 **自动化笔记同步机制**。

1. **自动同步脚本**：通过运行 `npm run sync` (即 `scripts/sync.ts`)，脚本会从外部的笔记仓库（默认尝试获取环境变量 `NOTES_REPO` 或同级目录下的 `notes-source`）中读取 Markdown 文档。
2. **元数据解析与归档**：
   - 脚本会自动解析并生成文档的 Frontmatter（包括日期、标题等）。如果文档没有设置，它会通过文件名和 Git 历史自动推断。
   - 博客的文章自动根据其所在的外层文件夹名称来进行**分类 (Category)**。文件名中的数字（如 `01-xxx.md`）能够自动被解析出以设定文章的排序（order）。
3. **资源处理与安全转义**：
   - 笔记引用的本地静态资源（如图片）会自动拷贝处理和路径修正。
   - 由于 VitePress 基于 Vue，代码内部的诸如 `-->` 的内容与部分 HTML 标签在 Markdown 内处理可能会出错，脚本会自动作转义处理以解决兼容性问题。
4. **生成静态路由**：处理后的文章及最终生成的分类元数据（`categories.json`）都会存放于 `generated/notes` 目录下，并最终配合 VitePress 进行页面的静态页面构建。

每次在运行本地服务（`npm run dev`）或打包部署（`npm run build`）前，该同步机制都会自动触发，保证博客展示内容的绝对最新。

## 项目结构
- `.vitepress/` - VitePress 配置文件目录。
- `scripts/sync.ts` - 核心的笔记同步处理脚本。
- `generated/notes/` - 自动化脚本实时处理后生成的博客源文件。
- `public/` - 放置如 `avatar.jpg` 头像等公共静态资源的目录。

