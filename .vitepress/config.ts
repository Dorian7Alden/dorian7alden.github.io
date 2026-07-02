import { defineConfig } from 'vitepress'
import { configureMarkdown } from '../scripts/markdown'

export default defineConfig({
  title: '双遥学长的个人博客',
  lang: 'zh-CN',
  base: '/',
  markdown: {
    mermaid: true,
    config: (md) => configureMarkdown(md),
  },
  head: [
    ['meta', { name: 'referrer', content: 'no-referrer' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap' }],
  ],
  themeConfig: {
    profile: {
      name: '代双遥',
      desc: '软件工程师',
      links: [
        { icon: 'simple-icons:github',   url: 'https://github.com/dorian7alden' },
        { icon: 'simple-icons:gitee',    url: 'https://gitee.com/dorian7alden' },
        { icon: 'simple-icons:bilibili', url: 'https://b23.tv/mgdrLOu' },
        { icon: 'mdi:email',             url: 'mailto:dorian7alden@gmail.com' },
      ],
    },
  },
})
