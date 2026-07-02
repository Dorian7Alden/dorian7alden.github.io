import type MarkdownIt from 'markdown-it'

// === 代码块增强（标题栏 + 折叠 + 复制按钮） ===

const COPY_ICON = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`

export function setupCodeBlock(md: MarkdownIt) {
  const defaultFence = md.renderer.rules.fence!
  let cbCounter = 0

  md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
    const token = tokens[idx]
    const langName = token.info.trim().split(/\s+/)[0] || ''

    // mermaid 代码块交给 mermaid 策略处理
    if (langName === 'mermaid') {
      return defaultFence(tokens, idx, options, env, slf)
    }

    cbCounter++
    const langLabel = langName || 'text'
    const uid = `cb-${cbCounter}`

    // Shiki 高亮
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
