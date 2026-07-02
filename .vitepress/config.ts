import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '双遥学长的个人博客',
  base: '/',
  head: [
    ['meta', { name: 'referrer', content: 'no-referrer' }],
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
