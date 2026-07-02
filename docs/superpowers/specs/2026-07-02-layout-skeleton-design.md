# 布局骨架重构设计

- **日期**: 2026-07-02
- **状态**: 已确认

## 目标

将博客布局分离为骨架层（Layout.vue）和实例层（Index.vue），让所有页面自动使用统一框架。

## 背景

当前 Index.vue 既是骨架又是首页实例——包含结构代码和首页卡片。其他页面设置了 `layout: false` 但未导入任何框架，处于裸渲染状态。需要一个纯骨架作为 VitePress 主题布局。

## 架构

```
Layout.vue（主题骨架）            Index.vue（首页实例）         其他页面
┌──────────────────────┐       ┌──────────────────┐       ┌──────────┐
│ Header               │       │ <Layout>         │       │ <Layout> │
├───────┬──────┬───────┤       │  #left:          │       │  自动渲染  │
│ slot  │<Cont │ slot  │  ←──  │    ProfileCard   │       │  md 内容  │
│ #left │ent />│ #right│       │    目录/其他卡片   │       │  进中栏    │
│       │      │       │       │  #right:         │       │           │
│       │Footer│       │       │    统计/推荐卡片   │       │           │
├───────┴──────┴───────┤       │ </Layout>        │       │ </Layout> │
└──────────────────────┘       └──────────────────┘       └──────────┘
```

- **Layout.vue**：纯骨架，Header + 三栏 grid + Footer，中栏用 `<Content />`，左右栏只有空 slot
- **Index.vue**：用 `<Layout>` 包裹，填充首页卡片
- **其他页面**：去掉 `layout: false`，自动由 Layout 包裹

## 文件变更

| 文件 | 动作 |
|------|------|
| `views/Layout.vue` | 重写为纯骨架 |
| `styles/layout.css` | 新建，从 index.css 迁移布局样式 |
| `views/Index.vue` | 重写为 Layout 包裹 + slot 填充 |
| `styles/index/index.css` | 删除 |
| `styles/index/profile-card.css` | 追加一条 `.card-profile-links svg` 规则（从 index.css 迁入） |
| `theme/index.ts` | Layout 导入路径不变（仍是 `./views/Layout.vue`） |
| `aboutme.md` 等 5 个 .md | 去掉 `layout: false` |
| `index.md` | 不变 |

## 样式拆分

- `styles/layout.css`：`.page` flex 容器、grid 三栏、`.col` / `.col-inner`、`.sidebar-card`、渐入动画
- `styles/index/profile-card.css`：追加 `.card-profile-links svg` 规则

## 接口

Layout.vue 对外暴露两个具名 slot：

| Slot | 位置 | 用途 |
|------|------|------|
| `#left` | 左栏 | 页面自定义左侧边栏内容 |
| `#right` | 右栏 | 页面自定义右侧边栏内容 |

中栏由 `<Content />` 渲染 md 页面内容，不暴露为 slot。
