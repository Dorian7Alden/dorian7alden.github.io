import type { Theme } from 'vitepress'
import Layout from './ThemeLayout.vue'
import './styles/base/global.css'
import './styles/markdown/blank-line.css'
import './styles/markdown/list.css'
import './styles/markdown/code-block.css'
import './styles/markdown/mermaid.css'

export default {
  Layout,
} satisfies Theme
