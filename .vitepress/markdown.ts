import type MarkdownIt from 'markdown-it'
import footnote from 'markdown-it-footnote'
import { full as emoji } from 'markdown-it-emoji'
import mark from 'markdown-it-mark'
import sub from 'markdown-it-sub'
import sup from 'markdown-it-sup'
import taskLists from 'markdown-it-task-lists'
import toc from 'markdown-it-toc-done-right'
import mathjax3 from 'markdown-it-mathjax3'

// === 空行注入 ===

function blankLineInject(md: MarkdownIt) {
  md.core.ruler.after('block', 'blank-line', (state) => {
    const newTokens = []

    for (let i = 0; i < state.tokens.length; i++) {
      const token = state.tokens[i]
      newTokens.push(token)

      if (!token.type.endsWith('_close') || !token.map) continue
      if (i >= state.tokens.length - 1) continue

      const nextToken = state.tokens[i + 1]
      if (!nextToken.map) continue

      const gapLines = nextToken.map[0] - token.map[1]
      const extraLines = gapLines - 1

      for (let j = 0; j < extraLines; j++) {
        const open = new state.Token('paragraph_open', 'p', 1)
        open.attrSet('class', 'blank-line')
        const inline = new state.Token('inline', '', 0)
        inline.content = ' '
        inline.children = []
        newTokens.push(open, inline)
        newTokens.push(new state.Token('paragraph_close', 'p', -1))
      }
    }

    state.tokens = newTokens
  })
}

// === 代码块增强（标题栏 + 折叠 + 行号 + 复制按钮） ===

const COPY_ICON = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`

function enhanceFence(md: MarkdownIt) {
  const defaultFence = md.renderer.rules.fence!
  let cbCounter = 0

  md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
    const token = tokens[idx]
    cbCounter++

    const langName = token.info.trim().split(/\s+/)[0] || ''
    const langLabel = langName || 'text'
    const uid = `cb-${cbCounter}`

    // Mermaid：输出原始预文本，交给客户端 Mermaid.js 渲染为 SVG
    if (langName === 'mermaid') {
      return `
        <div class="code-block code-block-mermaid language-mermaid">
          <input type="checkbox" id="${uid}" class="code-block-toggle" checked hidden>
          <div class="code-block-header">
            <span class="code-block-title">MERMAID</span>
          </div>
          <div class="code-block-body">
            <pre class="mermaid">${md.utils.escapeHtml(token.content)}</pre>
          </div>
        </div>`
    }

    // 普通代码块：Shiki 高亮
    const defaultHtml = defaultFence(tokens, idx, options, env, slf)
    const preMatch = defaultHtml.match(/<pre[\s\S]*?<\/pre>/i)
    const preBlock = preMatch ? preMatch[0] : `<pre><code>${md.utils.escapeHtml(token.content)}</code></pre>`

    return `
      <div class="code-block language-${langName}">
        <input type="checkbox" id="${uid}" class="code-block-toggle" checked hidden>
        <div class="code-block-header">
          <span class="code-block-title">${langLabel.toUpperCase()}</span>
          <span class="code-block-lang">${langLabel.toUpperCase()}</span>
          <button class="copy code-block-copy" title="复制代码">${COPY_ICON}</button>
        </div>
        <div class="code-block-body">
          ${preBlock}
        </div>
      </div>`
  }
}

// === 统一入口 ===

export function configureMarkdown(md: MarkdownIt) {
  blankLineInject(md)

  md.use(taskLists)           // - [ ] 任务列表
  md.use(footnote)            // [^id] 脚注
  md.use(emoji)               // :smile: emoji
  md.use(mark)                // ==高亮==
  md.use(sub)                 // ~下标~
  md.use(sup)                 // ^上标^
  md.use(toc, {               // [TOC] 目录
    containerClass: 'table-of-contents',
    listType: 'ul',
  })

  md.use(mathjax3)            // $inline$ $$block$$

  // 放在最后，确保 VitePress 的 Shiki fence renderer 已就位
  enhanceFence(md)
}
