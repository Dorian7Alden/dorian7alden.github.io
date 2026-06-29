import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'
import yaml from 'js-yaml'

const __dirname = dirname(fileURLToPath(import.meta.url))
const configPath = join(__dirname, '..', 'blog.config.yml')
const cfg = yaml.load(readFileSync(configPath, 'utf-8')) as any

export default defineConfig({
  base: cfg.site.base,
  title: cfg.site.title,
  description: cfg.site.description,
  lang: cfg.site.lang,
  cleanUrls: true,
  ignoreDeadLinks: true,

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: cfg.site.themeColor }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:title', content: cfg.site.title }],
    ['meta', { name: 'og:description', content: cfg.site.description }],
  ],

  markdown: {
    theme: {
      light: cfg.markdown.lightTheme,
      dark: cfg.markdown.darkTheme,
    },
    lineNumbers: cfg.markdown.lineNumbers,
  },

  themeConfig: {
    blog: {
      author: cfg.author,
      hero: cfg.hero,
      about: cfg.about,
    },

    nav: cfg.nav,

    socialLinks: [
      { icon: 'github', link: `https://github.com/${cfg.author.github}` },
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: cfg.footer.message,
      copyright: cfg.footer.copyright,
    },

    sidebar: {},

    outline: {
      level: [2, 3],
      label: '目录',
    },

    docFooter: {
      prev: cfg.labels.docFooter.prev,
      next: cfg.labels.docFooter.next,
    },
    darkModeSwitchLabel: cfg.labels.darkModeSwitch,
    sidebarMenuLabel: cfg.labels.sidebarMenu,
    returnToTopLabel: cfg.labels.returnToTop,
  },
})
