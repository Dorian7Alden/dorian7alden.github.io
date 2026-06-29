# Blog Config File Design

## Context

The project has hardcoded personalization parameters spread across three locations:
- `.vitepress/config.ts` — site metadata, nav, footer, labels
- `.vitepress/theme/components/HeroSection.vue` — hero text, topic pills
- `.vitepress/theme/components/AboutPage.vue` — author name, skills, bio
- `scripts/sync.ts` — notes repo path, content dir

Extract these into a single `blog.config.yml` so changing name, social links, skill tags, or sync paths doesn't require hunting through source files.

## Approach

Central YAML + VitePress themeConfig data flow (Approach A).

```
blog.config.yml
      ├─► .vitepress/config.ts   — fs + js-yaml read, spread into defineConfig + themeConfig.blog
      ├─► scripts/sync.ts        — fs + js-yaml read sync.*
      └─► Vue components         — useData().theme.blog
```

## YAML Structure

Single file at repo root: `blog.config.yml`

```yaml
site:
  title: "Dorian's Blog"
  description: '技术学习笔记与经验分享 — Dorian Alden Dai'
  lang: zh-CN
  base: /
  themeColor: '#5C6AC4'

author:
  name: Dorian Alden Dai
  github: Dorian7Alden
  avatar: /avatar.jpg
  bio: 软件工程专业学生，关注后端工程、AI 工具与持续学习实践。

nav:
  - text: 首页
    link: /
  - text: 分类
    link: /categories
  - text: 关于
    link: /about

footer:
  message: 记录学习，分享技术
  copyright: Copyright © 2026 Dorian Alden Dai

hero:
  kicker: Dorian7Alden · Tech Notes
  title: 记录工程实践，沉淀技术成长
  tagline: 这里整理 Java、后端工程、AI 工具和学习实践中的真实笔记，把零散经验沉淀成可复用的知识卡片。
  topics:
    - Java
    - Spring
    - AI Tools
    - Git

about:
  blogTitle: 关于本站
  blogDescription:
    - 这个博客记录我的技术学习笔记...
    - 我希望这里不只是文章列表...
  focusTitle: 技术方向
  skills:
    - Java
    - Spring Boot
    - Spring Cloud
    - MySQL
    - Redis
    - Git
    - Docker
    - CI/CD
    - Vue 3
    - VitePress
    - AI Tools

markdown:
  lightTheme: github-light
  darkTheme: github-dark
  lineNumbers: true

labels:
  docFooter:
    prev: 上一篇
    next: 下一篇
  darkModeSwitch: 深色模式
  sidebarMenu: 菜单
  returnToTop: 返回顶部

sync:
  notesRepo: /home/dorian/repo/kualk-learn-notes
  contentDir: generated/notes
```

## Files Changed

### New: `blog.config.yml`
All configurable parameters in one place.

### `.vitepress/config.ts`
- Import `fs`, `path`, `js-yaml`
- Read `blog.config.yml` at the top
- Replace all hardcoded strings with config values
- Place `author`, `hero`, `about`, `labels` under `themeConfig.blog` for Vue component access

### `scripts/sync.ts`
- Import `js-yaml` (already a dependency)
- Read `blog.config.yml`
- Replace hardcoded `NOTES_REPO` fallback chain and `CONTENT_DIR` with `config.sync.*`
- Keep env var overrides (`NOTES_REPO`, `CONTENT_DIR`) as higher priority than config file

### `HeroSection.vue`
- Import `useData` from `vitepress`
- Replace hardcoded kicker, title, tagline, topics, panel name/desc with `theme.blog.hero.*` and `theme.blog.author.*`

### `AboutPage.vue`
- Import `useData` from `vitepress`
- Replace hardcoded name, bio, GitHub link, skills, blog description with `theme.blog.about.*` and `theme.blog.author.*`

## Data Flow

```
┌─────────────────────────────────────────────────────┐
│ blog.config.yml                                     │
│                                                     │
│ site ──────────► defineConfig({ title, description })│
│ author ────────► themeConfig.blog.author             │
│ nav ───────────► themeConfig.nav                     │
│ footer ────────► themeConfig.footer                  │
│ hero ──────────► themeConfig.blog.hero               │
│ about ─────────► themeConfig.blog.about              │
│ labels ────────► themeConfig.blog.labels             │
│ markdown ──────► markdown config                     │
│ sync ──────────► scripts/sync.ts (direct read)       │
└─────────────────────────────────────────────────────┘
```

## Types

Add a `BlogConfig` interface in a shared types file or inline in config.ts:

```ts
interface BlogConfig {
  site: { title, description, lang, base, themeColor }
  author: { name, github, avatar, bio }
  nav: { text, link }[]
  footer: { message, copyright }
  hero: { kicker, title, tagline, topics: string[] }
  about: { blogTitle, blogDescription: string[], focusTitle, skills: string[] }
  markdown: { lightTheme, darkTheme, lineNumbers }
  labels: { docFooter: { prev, next }, darkModeSwitch, sidebarMenu, returnToTop }
  sync: { notesRepo, contentDir }
}
```

## Verification

1. `npm run dev` — site starts without errors
2. Homepage renders hero section with correct text, topics, stats
3. `/about` renders name, skills, bio from config
4. `/categories` works as before
5. Change a value in `blog.config.yml` (e.g. author name), restart dev server, confirm the change appears
6. `npm run build` — production build succeeds
7. `npm run sync` — sync script reads config and processes notes correctly
