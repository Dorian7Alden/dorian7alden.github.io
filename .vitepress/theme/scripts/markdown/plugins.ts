import type MarkdownIt from 'markdown-it'
import footnote from 'markdown-it-footnote'
import { full as emoji } from 'markdown-it-emoji'
import mark from 'markdown-it-mark'
import sub from 'markdown-it-sub'
import sup from 'markdown-it-sup'
import taskLists from 'markdown-it-task-lists'
import toc from 'markdown-it-toc-done-right'
import mathjax3 from 'markdown-it-mathjax3'

// === markdown-it 插件注册 ===

export function registerPlugins(md: MarkdownIt) {
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
}
