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

```
dorian7alden.github.io/
├── .vitepress/
│   ├── config.ts                    # VitePress 站点配置（读取 blog.config.yml）
│   └── theme/
│       ├── index.ts                 # 主题入口 — 注册全局组件
│       ├── style.css                # 全局设计系统（CSS 自定义属性、排版、布局）
│       ├── CustomLayout.vue         # 自定义布局容器（阅读进度、回到顶部、笔记树）
│       └── components/
├── docs/
├── generated/
│   └── notes/
├── scripts/
│   └── sync.ts                      # 核心同步脚本 — 从外部笔记仓库处理并生成内容
├── about.md                         # 关于页面入口（渲染 AboutPage 组件）
├── blog.config.yml                  # 中央 YAML 配置（站点、作者、导航、Hero、标签、同步）
├── categories.md                    # 分类页面入口（渲染 CategoriesPage 组件）
├── CNAME                            # 自定义域名：dorian7.com
├── index.md                         # 首页（渲染 HeroSection + PostList）
└── README.md                        # 项目文档（本文件）
```

## 核心文件夹说明

- **`.vitepress/`** — VitePress 配置与自定义主题目录。`config.ts` 读取 `blog.config.yml` 生成站点配置；`theme/` 下包含完整的设计系统（`style.css`）和 9 个 Vue 组件，覆盖首页、文章列表、分类浏览、笔记树、阅读进度等全部 UI 元素。
- **`scripts/sync.ts`** — 核心自动化笔记同步脚本。运行时从外部笔记仓库（通过环境变量 `NOTES_REPO` 或 `blog.config.yml` 中的 `sync.notesRepo` 指定）读取 Markdown 文件，解析 Frontmatter、按文件夹自动分类、处理本地资源路径、转义 Vue 不兼容语法，最终将处理结果输出到 `generated/notes/`。
- **`generated/notes/`** — 自动化脚本生成的博客源文件目录。`categories.json` 是唯一的全局数据源，被所有前端组件通过 `import.meta.glob` 导入。该目录及其所有内容均由 `scripts/sync.ts` 自动生成，**请勿手动编辑**。目前包含 16 个分类目录、共 277 篇文章。
- **`public/`** — 静态资源目录。其中的文件（头像 `avatar.jpg`、站点图标 `favicon.svg`）直接映射到站点根路径，可用于 HTML `<head>` 引用。
- **`.github/workflows/`** — GitHub Actions CI/CD 部署配置。当 `main` 或 `notes` 分支收到推送时，自动检出博客源码和笔记源码，执行同步和构建，最后部署到 GitHub Pages。

## 核心文件说明

- **`blog.config.yml`** — 中央配置文件，同时被 `scripts/sync.ts` 和 `.vitepress/config.ts` 读取。包含站点元信息、作者信息、导航栏、页脚、Hero 区域、关于页面、Markdown 主题以及同步路径等全部可配置项。修改后重新运行 `npm run dev` 即可生效。
- **`about.md` / `categories.md`** — VitePress 页面入口文件。通过简洁的 Frontmatter 和 Vue 组件标签（`<AboutPage />`、`<CategoriesPage />`）实现页面渲染，组件实现在 `.vitepress/theme/components/` 中。
- **`CNAME`** — 自定义域名配置文件。GitHub Pages 读取此文件将站点绑定到 `dorian7.com`。

