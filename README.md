---
create-time: 2026-05-06
update-time: 2026-07-01
author: Dorian Alden
---

# Dorian's Blog

## 简介

基于 VitePress + Vue 3 + TypeScript 构建的个人技术博客。

## 快速开始

```bash
git clone git@github.com:dorian7alden/dorian7alden.github.io.git
cd dorian7alden.github.io
npm install
npm run dev      # 启动开发服务器 → http://localhost:5173
npm run build    # 构建生产版本
npm run preview  # 预览构建产物
```

## 项目结构

```
dorian7alden.github.io/
├── .vitepress/
│   ├── config.ts                # VitePress 站点配置（标题、base 路径等）
│   └── theme/
│       ├── index.ts             # 主题入口，注册自定义布局组件
│       ├── views/               # 页面级 Vue 组件（每个路由对应一个页面组件）
│       ├── components/          # 可复用的子组件
│       ├── assets/              # 静态资源（头像、图标等）
│       ├── styles/              # 全局与组件样式
│       └── scripts/             # 主题侧辅助脚本
├── index.md                     # 首页 → 路由 /
├── notes/                       # 博客笔记内容
│   ├── archives/                # 已归档笔记
│   ├── inboxes/                 # 待整理笔记
│   └── references/              # 参考资料
├── _docs/                       # 项目自身文档
│   └── 01-dev-spec.md           # 开发规范
├── package.json                 # 依赖与 npm 脚本
├── tsconfig.json                # TypeScript 配置
├── CLAUDE.md                    # Claude Code 项目指令
```

## 开发规范

- 分模块开发，按页面分组分文件夹
- 每个 Markdown 文件必须包含 frontmatter 元数据：
  - `create-time: YYYY-MM-DD`
  - `update-time: YYYY-MM-DD`

详见 `_docs/01-dev-spec.md`。

## 技术栈

- [VitePress](https://vitepress.dev/) — 静态站点生成器
- [Vue 3](https://vuejs.org/) — UI 框架
- [TypeScript](https://www.typescriptlang.org/) — 类型安全
