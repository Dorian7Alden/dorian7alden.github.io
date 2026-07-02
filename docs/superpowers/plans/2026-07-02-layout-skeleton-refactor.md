# 布局骨架重构 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Index.vue 拆分为纯骨架 Layout.vue + 首页实例 Index.vue，让所有非首页 md 页面自动使用 Layout 框架。

**Architecture:** Layout.vue 注册为 VitePress 主题布局，用 `<Content />` 渲染 md 内容到中栏；Index.vue 用 `<Layout>` 包裹，通过 `#left` / `#right` slot 填充首页侧边栏卡片。

**Tech Stack:** VitePress + Vue 3 + TypeScript

## Global Constraints

- 布局框架放在 `views/Layout.vue`，样式放 `styles/layout.css`
- 所有 .md 页面 `layout: false` 仅保留 index.md
- Vue 组件导入必须带 `.vue` 扩展名
- 禁止在 Vue 文件中直接写样式，样式统一写 `.css` 文件再导入
- 不引入不必要的抽象和过度设计

---

### Task 1: 新建 layout.css（从 index.css 提取布局样式）

**Files:**
- Create: `.vitepress/theme/styles/layout.css`

**Interfaces:**
- Produces: 供 Layout.vue 导入的布局样式，定义 `.page`、`.body`、`.col`、`.col-inner`、`.sidebar-card`、`fade-in-up` 动画

- [ ] **Step 1: 创建 layout.css**

将当前 `styles/index/index.css` 中的布局结构样式完整提取，排除 `.card-profile-links svg`（该规则会在 Task 4 迁入 profile-card.css）。

写入 `.vitepress/theme/styles/layout.css`：

```css
.page {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 50px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* === page-load animation === */
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.page-header,
.body,
.sidebar-card {
  animation-name: fade-in-up;
  animation-duration: 0.3s;
  animation-fill-mode: both;
  animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
}

.page-header                          { animation-delay: 0s;    }
.body                                 { animation-delay: 0.05s; }

.col-left  .sidebar-card:nth-child(1) { animation-delay: 0.10s; }
.col-left  .sidebar-card:nth-child(2) { animation-delay: 0.14s; }
.col-left  .sidebar-card:nth-child(3) { animation-delay: 0.18s; }

.col-right .sidebar-card:nth-child(1) { animation-delay: 0.22s; }
.col-right .sidebar-card:nth-child(2) { animation-delay: 0.26s; }

@media (prefers-reduced-motion: reduce) {
  .page-header, .body, .sidebar-card {
    animation: none;
  }
}

/* header */
.page-header {
  flex-shrink: 0;
  height: 70px;
  background: var(--color-surface);
  border-radius: 0 0 var(--radius) var(--radius);
  padding: 0 24px;
}

/* body */
.body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 4.5fr 1.3fr;
  gap: 16px;
}
.col {
  min-height: 0;
}
.col-inner {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 24px;
  height: 100%;
}

.col-left .col-inner,
.col-right .col-inner {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: transparent;
  padding: 0;
}

.sidebar-card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 12px;
  font-size: 0.9rem;
  color: var(--color-muted);
}
```

- [ ] **Step 2: 提交**

```bash
git add .vitepress/theme/styles/layout.css
git commit -m "feat: 新建 layout.css，从 index.css 提取布局样式"
```

---

### Task 2: 重写 Layout.vue 为纯骨架

**Files:**
- Modify: `.vitepress/theme/views/Layout.vue`

**Interfaces:**
- Consumes: `styles/layout.css`（Task 1）、`Header.vue`、`Footer.vue`、`vitepress` 的 `<Content />`
- Produces: VitePress 主题布局组件，暴露 `#left` 和 `#right` 具名 slot

- [ ] **Step 1: 重写 Layout.vue**

用以下内容完全替换 `.vitepress/theme/views/Layout.vue`：

```vue
<template>
  <div class="page">
    <Header class="page-header" />

    <main class="body">

      <aside class="col col-left">
        <div class="col-inner">
          <slot name="left" />
        </div>
      </aside>

      <section class="col col-center">
        <div class="col-inner">
          <Content />
          <Footer />
        </div>
      </section>

      <aside class="col col-right">
        <div class="col-inner">
          <slot name="right" />
        </div>
      </aside>

    </main>
  </div>
</template>

<script setup>
import { Content } from 'vitepress'
import Header from '../components/Header.vue'
import Footer from '../components/Footer.vue'
</script>

<style>
@import '../styles/layout.css';
</style>
```

- [ ] **Step 2: 提交**

```bash
git add .vitepress/theme/views/Layout.vue
git commit -m "ref: 重写 Layout.vue 为纯布局骨架"
```

---

### Task 3: 重写 Index.vue 为 Layout 实例

**Files:**
- Modify: `.vitepress/theme/views/Index.vue`

**Interfaces:**
- Consumes: `Layout.vue`（Task 2）、`ProfileCard.vue`
- Produces: 首页实例组件，向 Layout 的 `#left` 和 `#right` slot 填充卡片

- [ ] **Step 1: 重写 Index.vue**

用以下内容完全替换 `.vitepress/theme/views/Index.vue`：

```vue
<template>
  <Layout>
    <template #left>
      <ProfileCard />

      <div class="sidebar-card">
        目录<br/><br/><br/><br/>
      </div>

      <div class="sidebar-card">
        其他信息<br/><br/><br/><br/>
      </div>
    </template>

    <template #right>
      <div class="sidebar-card">
        统计<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
      </div>

      <div class="sidebar-card">
        推荐<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
      </div>
    </template>
  </Layout>
</template>

<script setup>
import Layout from '../views/Layout.vue'
import ProfileCard from '../components/index/ProfileCard.vue'
</script>
```

注意：Index.vue 不再需要 `<style>` 块，布局样式由 Layout.vue 导入的 `layout.css` 提供，`.sidebar-card` 样式也已在 `layout.css` 中定义。

- [ ] **Step 2: 提交**

```bash
git add .vitepress/theme/views/Index.vue
git commit -m "ref: 重写 Index.vue 为 Layout 骨架的首页实例"
```

---

### Task 4: 更新 profile-card.css + 删除 index.css

**Files:**
- Modify: `.vitepress/theme/styles/index/profile-card.css`
- Delete: `.vitepress/theme/styles/index/index.css`

**Interfaces:**
- Consumes: 当前 `styles/index/index.css` 中唯一的非布局规则 `.card-profile-links svg`
- Produces: 完整的 profile-card 样式文件，不再需要 index.css

- [ ] **Step 1: 在 profile-card.css 末尾追加 `.card-profile-links svg` 规则**

在当前文件末尾追加：

```css
.card-profile-links svg {
  width: 20px;
  height: 20px;
}
```

- [ ] **Step 2: 删除 index.css**

```bash
rm .vitepress/theme/styles/index/index.css
```

- [ ] **Step 3: 提交**

```bash
git add .vitepress/theme/styles/index/profile-card.css
git rm .vitepress/theme/styles/index/index.css
git commit -m "ref: 迁入 .card-profile-links svg 规则至 profile-card.css，删除 index.css"
```

---

### Task 5: 移除非首页 .md 文件的 layout: false

**Files:**
- Modify: `aboutme.md`
- Modify: `notes.md`
- Modify: `projects.md`
- Modify: `resources.md`
- Modify: `recommendations.md`

**Interfaces:**
- Consumes: Layout.vue（Task 2）作为 VitePress 主题布局
- Produces: 5 个页面由 Layout 自动包裹，`layout: false` 仅保留在 index.md

- [ ] **Step 1: 移除 aboutme.md 的 layout: false**

删除 frontmatter 中的 `layout: false` 行。文件变为：

```markdown
---
---

关于我
```

- [ ] **Step 2: 移除 notes.md 的 layout: false**

删除 frontmatter 中的 `layout: false` 行。文件变为：

```markdown
---
---

笔记总览页
```

- [ ] **Step 3: 移除 projects.md 的 layout: false**

文件变为：

```markdown
---
---

项目总览页
```

- [ ] **Step 4: 移除 resources.md 的 layout: false**

文件变为：

```markdown
---
---

资源分享页
```

- [ ] **Step 5: 移除 recommendations.md 的 layout: false**

文件变为：

```markdown
---
---

个人推荐页
```

- [ ] **Step 6: 提交**

```bash
git add aboutme.md notes.md projects.md resources.md recommendations.md
git commit -m "feat: 非首页页面移除 layout:false，自动使用 Layout 框架"
```

---

### Task 6: 验证

**Files:**
- 无文件变更，仅验证

- [ ] **Step 1: 构建项目检查无报错**

```bash
npm run build
```

预期：构建成功，无 VitePress 或 Vue 编译错误。

- [ ] **Step 2: 启动开发服务器目视检查**

```bash
npm run dev
```

逐页检查：
- `/` — 首页，应显示 Header + 三栏布局 + Footer + ProfileCard 及各占位卡片
- `/aboutme` — 应显示 Header + 正文"关于我"居中栏 + Footer，左右栏为空
- `/notes` — 同上，"笔记总览页"
- `/projects` — 同上，"项目总览页"
- `/resources` — 同上，"资源分享页"
- `/recommendations` — 同上，"个人推荐页"

所有页面应有渐入动画，深色/浅色切换正常。

- [ ] **Step 3: 确认无遗留引用**

```bash
grep -rn "index/index.css" .vitepress/ . --include="*.vue" --include="*.ts" --include="*.css" 2>/dev/null | grep -v node_modules
```

预期：无输出（无文件再引用已删除的 index.css）。
