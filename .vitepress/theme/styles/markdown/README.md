# Markdown 样式策略

按视觉功能拆分，每个文件覆盖一类 markdown 渲染样式的 CSS。

## 文件对照

| CSS 文件 | 覆盖范围 | 对应解析策略 |
|----------|----------|-------------|
| `blank-line.css` | 空行视觉渲染（`p.blank-line`） | `scripts/markdown/blank-line.ts` |
| `list.css` | 通用列表（`ul, ol, li`）+ 任务列表（`.task-list-item`） | `scripts/markdown/plugins.ts`（taskLists）+ 通用 markdown |
| `code-block.css` | 代码块增强（标题栏/折叠/复制/行号）、行内代码、Shiki 语法高亮颜色、裸 `<pre>` 代码块 | `scripts/markdown/code-block.ts` + 通用 markdown |
| `mermaid.css` | Mermaid 图表容器（`.code-block-mermaid`） | `scripts/markdown/mermaid.ts` + `scripts/markdown/mermaid-client.ts` |

## 设计原则

- **按视觉功能分组**，不机械地跟解析策略一一对应。例如"列表"和"任务列表"在视觉上都属于列表类，放同一个文件
- `.code-block` 是 CSS 组件级的样式系统，内部有变量、容器、子元素层级关系，保持在一个文件中便于维护
- Mermaid 图表样式独立，因为它在视觉上跟普通代码块有显著差异（透明背景、居中、SVG 适配）

## 新增渲染策略时的指引

1. 在 `scripts/markdown/` 下新增策略文件
2. 如果该策略涉及新的视觉呈现，在 `styles/markdown/` 下新增对应的 CSS 文件
3. 在 `.vitepress/theme/index.ts` 中导入新的 CSS 文件
4. 更新本 README 的对照表
