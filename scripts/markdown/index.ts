import type MarkdownIt from 'markdown-it'
import { blankLineInject } from './blank-line'
import { registerPlugins } from './plugins'
import { setupCodeBlock } from './code-block'
import { setupMermaidFence } from './mermaid'

// === 统一入口 ===

export function configureMarkdown(md: MarkdownIt) {
  blankLineInject(md)
  registerPlugins(md)
  setupCodeBlock(md)
  setupMermaidFence(md)
}
