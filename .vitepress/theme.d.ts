import 'vitepress'

declare module 'vitepress' {
  interface Config {
    themeConfig?: {
      profile?: {
        name: string
        desc: string
        links: { icon: string; url: string }[]
      }
    }
  }
}
