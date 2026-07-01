# 语言
- 全程中文交流

# 项目
- 基于 VitePress + Vue 3 + TypeScript 的个人技术博客
- 全自定义 UI 路线：所有 md 页面 `layout: false`，不用 VitePress 默认主题，自己写结构和样式
- VitePress 仅作为静态站点生成器 + 开发工具链（文件路由、md→HTML、HMR、构建）

# 开发规范
- 分模块开发，按页面分组分文件夹
- 每个 Markdown 文件必须包含 frontmatter：`create-time: YYYY-MM-DD` 和 `update-time: YYYY-MM-DD`
- Vue 组件导入必须带 `.vue` 扩展名

# 风格
- 不引入不必要的抽象和过度设计
