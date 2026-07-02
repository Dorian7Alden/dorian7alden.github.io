# Markdown 渲染策略

所有 markdown-it 解析/渲染的定制逻辑，每个策略独立一个文件，通过 `index.ts` 统一注册到 VitePress markdown 管道。

依赖 `markdown-it` 的 plugin / ruler / renderer 机制。统一入口是 `configureMarkdown(md: MarkdownIt)`，在 `.vitepress/config.ts` 中通过 `markdown.config` 回调调用。

---

## 文件一览

| 文件 | 类型 | 职责 | 机制 |
|------|------|------|------|
| `index.ts` | 入口 | 统一入口，编排各策略注册顺序 | 顺序调用各模块导出函数，被 `.vitepress/config.ts` 导入 |
| `blank-line.ts` | 服务端 | 在相邻块级元素之间插入空行 `<p>` 节点 | `md.core.ruler` 自定义 rule（`block` 阶段之后触发） |
| `plugins.ts` | 服务端 | 批量注册 markdown-it 第三方插件 | `md.use()` |
| `code-block.ts` | 服务端 | 代码块 UI 增强：标题栏、折叠、复制按钮、行号 | 覆盖 `md.renderer.rules.fence`（对 `mermaid` 语言透传） |
| `mermaid.ts` | 服务端 | 构建时将 mermaid 代码块渲染为 `<pre class="mermaid">` 占位容器 | 覆盖 `md.renderer.rules.fence`（对非 mermaid 语言透传） |
| `mermaid-client.ts` | 客户端 | 浏览器端驱动 mermaid 解析，将占位容器渲染为 SVG | Vue composable（`onMounted` + `watch` router） |

---

## 设计原则

### 策略文件单一职责

每个 `.ts` 文件只做一类事情：空行注入只操作 token stream，代码块增强只覆写 fence renderer，插件注册只调用 `md.use()`。新功能不应往现有文件里塞，而是新增独立文件。

### 责任链模式处理 fence 冲突

`code-block.ts` 和 `mermaid.ts` 都覆盖 `md.renderer.rules.fence`，通过存储前一个 handler 形成调用链：

```
code-block → mermaid → 原始 VitePress fence (Shiki)
```

每个 handler 只处理自己关心的 `langName`，其余透传给上一个：

- `code-block.ts`：遇到 `mermaid` 语言时透传，其余自己处理
- `mermaid.ts`：只处理 `mermaid` 语言，其余透传

### 注册顺序即包裹顺序

`configureMarkdown` 中的调用顺序决定了策略的执行时序：

```
blank-line → plugins → code-block → mermaid
```

- `blank-line` 最先操作 token stream
- `mermaid` 在最外层包裹 fence 输出
- 调整顺序需评估对每个策略的影响

### 客户端/服务端严格隔离

`mermaid-client.ts` 是唯一位于 `scripts/markdown/` 但运行在浏览器端的代码。它使用 `useRouter()`（VitePress 客户端 API），因此 **不能** 出现在 `configureMarkdown` 的导入链中——`.vitepress/config.ts` 运行在 Node.js 环境，没有 `useRouter`。

必须通过 Vue 组件侧（`ThemeLayout.vue`）单独导入并调用。新增策略若涉及客户端运行时逻辑（如浏览器 API、Vue lifecycle），也应拆分独立的客户端文件，遵循同样的隔离规则。

---

## 新增渲染策略

1. **创建策略文件** — 在 `scripts/markdown/` 下创建 `.ts` 文件，导出一个签名符合 `(md: MarkdownIt) => void` 的函数
2. **注册到统一入口** — 在 `index.ts` 中导入该函数，在 `configureMarkdown` 中的合适位置调用（注意时序依赖）
3. **如果覆盖 fence** — 采用责任链模式：在函数内部保存当前的 `md.renderer.rules.fence`，仅处理目标 `langName`，其余调用原 handler
4. **如果需要客户端运行时** — 将客户端代码拆分到独立文件（如 `xxx-client.ts`），不经过 `index.ts` 的导入链，由 Vue 组件侧按需导入
5. **调整样式侧** — 如果引入新的视觉元素，在 `styles/markdown/` 下新增 CSS 文件，并在 `theme/index.ts` 中导入
6. **更新文档** — 更新本 README 的文件一览表和 `styles/markdown/README.md` 的对照表

---

## 与视觉侧的对应关系

| 策略文件 | 样式文件 | 说明 |
|----------|----------|------|
| `blank-line.ts` | `blank-line.css` | `p.blank-line` 空行占位样式 |
| `plugins.ts` | `list.css` | 通用列表 + 任务列表样式 |
| `code-block.ts` | `code-block.css` | 代码块标题栏、折叠、复制、行号、语法高亮、行内代码、裸 `<pre>` |
| `mermaid.ts` + `mermaid-client.ts` | `mermaid.css` | Mermaid 图表容器（透明背景、居中、SVG 适配） |

详见 `.vitepress/theme/styles/markdown/README.md`
