import type MarkdownIt from 'markdown-it'

// === 构建时：markdown-it fence 规则 ===

let mermaidCounter = 0

export function setupMermaidFence(md: MarkdownIt) {
  const defaultFence = md.renderer.rules.fence!

  md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
    const token = tokens[idx]
    const langName = token.info.trim().split(/\s+/)[0] || ''

    if (langName !== 'mermaid') {
      return defaultFence(tokens, idx, options, env, slf)
    }

    mermaidCounter++
    const uid = `mermaid-${mermaidCounter}`

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
}
