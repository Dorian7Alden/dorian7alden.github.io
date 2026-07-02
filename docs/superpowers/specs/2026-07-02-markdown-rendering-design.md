# Markdown 格式渲染支持方案

## 目标

让 VitePress 完整支持 Typora 编辑器的所有 Markdown 渲染效果，包括特殊格式（脚注、emoji、数学公式等）和空行视觉渲染。所有配置集中在 `.vitepress/markdown.ts` 统一管理，为后续自定义渲染规则提供扩展点。

## 文件变更

```
.vitepress/
  markdown.ts        ← 新建，唯一的 markdown 配置入口
  config.ts          ← 修改，新增 markdown 配置块，导入 markdown.ts
  theme/
    styles/
      base/
        markdown.css ← 新建，markdown 渲染相关样式（当前只有空行规则）
```

## 插件清单

| 插件 | 语法 | 用途 |
|------|------|------|
| `markdown-it-footnote` | `[^id]` | 脚注 |
| `markdown-it-emoji` | `:smile:` | Emoji 表情 |
| `markdown-it-mark` | `==text==` | 文字高亮 |
| `markdown-it-sub` | `~text~` | 下标 |
| `markdown-it-sup` | `^text^` | 上标 |
| `markdown-it-toc-done-right` | `[TOC]` | 自动目录 |
| `markdown-it-mathjax3` | `$...$` `$$...$$` | 数学公式（LaTeX） |

Mermaid 通过 VitePress 内置配置 `markdown: { mermaid: true }` 开启，无需额外插件。

### 依赖安装

```bash
npm i markdown-it-footnote markdown-it-emoji markdown-it-mark \
      markdown-it-sub markdown-it-sup markdown-it-toc-done-right \
      markdown-it-mathjax3
```

## 架构设计

### `markdown.ts` — 唯一入口

```ts
import type MarkdownIt from 'markdown-it'
import footnote from 'markdown-it-footnote'
// ... 其余 import

export function configureMarkdown(md: MarkdownIt) {
  // 预处理：注入空行标记（preprocess）
  // 符号型插件优先
  md.use(footnote)       // 脚注
  md.use(emoji)          // emoji
  md.use(mark)           // ==高亮==
  md.use(sub)            // ~下标~
  md.use(sup)            // ^上标^
  md.use(toc, { ... })   // [TOC]
  md.use(mathjax3)       // 最后：避免被其他插件干扰
}
```

### 空行预处理

在 `md.use()` 调用之前，通过 markdown-it 的 normalize 或 core rule 对原始文本做预处理：

- 检测 3+ 连续换行（即 ≥2 个空行）
- 保留第一个 `\n\n`（标准段落分隔）
- 剩余的每个空行替换为 `<p class="blank-line">&nbsp;</p>`

```css
/* markdown.css — 空行视觉样式 */
p.blank-line {
  height: 1em;
  margin: 0;
}
```

### 插件注册顺序理由

1. **footnote 最前**：需要优先解析 `[^id]` 语法，避免与其他插件冲突
2. **emoji → mark → sub → sup → toc**：符号型插件，互不干扰
3. **mathjax3 最后**：其 `$` 分隔符可能被其他插件误匹配，放最后最小化干扰
4. **后续扩展**：只需在函数体内追加 `md.use(...)` 或 `md.renderer.rules['xxx'] = ...`

## 验收标准

运行 `npm run dev` 访问 sample-md.md，逐项检查：

| # | 检查项 | 期望结果 |
|---|--------|----------|
| 1 | `==高亮==` | 文字黄色/高亮背景 |
| 2 | `^上标^` `~下标~` | 正确上浮/下沉 |
| 3 | `[^1]` 脚注 | 底部显示内容，点击跳转 |
| 4 | `:smile:` | 显示 emoji 图标 |
| 5 | `$E=mc^2$` 行内公式 | 正确渲染数学符号 |
| 6 | `$$...$$` 块级公式 | 居中显示，公式正确 |
| 7 | `[TOC]` | 自动生成目录列表 |
| 8 | ` ```mermaid ` | 渲染为流程图 |
| 9 | `::: tip/warning` | 显示彩色提示框（VitePress 内置） |
| 10 | `<kbd>` `<details>` | HTML 正确透传 |
| 11 | 3+ 连续空行 | 空行区域在视觉上呈现为一个空白行（约 1em 高度） |

## 非目标

- 自定义容器样式美化（当前 VitePress 默认样式足够）
- Typora 专有语法如 inline math 的不同写法
- 黑暗模式下的公式颜色适配（公式渲染后默认可读即可）
