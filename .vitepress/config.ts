import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/',
  title: "Dorian's Blog",
  description: '技术学习笔记与经验分享 — Dorian Alden Dai',
  lang: 'zh-CN',
  cleanUrls: true,
  ignoreDeadLinks: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#5C6AC4' }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:title', content: "Dorian's Blog" }],
    ['meta', { name: 'og:description', content: '技术学习笔记与经验分享' }],
  ],

  markdown: {
    theme: {
      light: 'github-light',
      dark: 'github-dark',
    },
    lineNumbers: true,
  },

  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '分类', link: '/categories' },
      { text: '关于', link: '/about' },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Dorian7Alden' },
    ],
    search: {
      provider: 'local',
    },
    footer: {
      message: '记录学习，分享技术',
      copyright: 'Copyright © 2026 Dorian Alden Dai',
    },
    sidebar: {},
    outline: {
      level: [2, 3],
      label: '目录',
    },
    docFooter: {
      prev: '上一篇',
      next: '下一篇',
    },
    darkModeSwitchLabel: '深色模式',
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '返回顶部',
  },
})
