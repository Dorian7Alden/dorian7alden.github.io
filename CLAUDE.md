# 语言
- 全程中文交流

# 项目
- 基于 VitePress + Vue 3 + TypeScript 的个人技术博客
- 全自定义 UI 路线：不使用 VitePress 默认主题，自己写结构和样式
- VitePress 仅作为静态站点生成器 + 开发工具链（文件路由、md→HTML、HMR、构建）

# 布局架构
- 分层设计：骨架层（`theme/Layout.vue`）→ 主题入口（`theme/ThemeLayout.vue`）→ 页面实例（`theme/views/Index.vue` 等）
- **Layout.vue**（纯骨架，位于 `theme/` 根目录）：Header + 三栏 CSS Grid `1fr 4.5fr 1.3fr` + Footer，最大宽度 1440px
  - 只划分区域，不包含任何业务内容——Header、Footer 是仅有的固定组件
  - 暴露三个 slot：`#left`（左栏）、默认 slot（中栏）、`#right`（右栏），无默认内容
  - 中栏默认 slot 下方固定包含 Footer
- **ThemeLayout.vue**（VitePress 主题入口，位于 `theme/` 根目录）：将 `<Content />` 注入 Layout 的默认 slot，注册为 VitePress 主题布局
- 页面实例（位于 `theme/views/`）：各页面按需使用 Layout 骨架填充内容，如 Index.vue
- 页面接入方式：
  - 普通页面：直接由 ThemeLayout 自动包裹，md 内容进中栏，左右栏为空
  - 需自定义侧边栏的页面：设 `layout: false`，手动导入 `theme/Layout.vue` 并填充 slot（参考 index.md）
- 当前状态：index.md 手动使用 Index.vue，其他页面（aboutme、notes、projects、recommendations、resources）由 ThemeLayout 自动包裹

# 开发规范
- 分模块开发，按页面分组分文件夹
- 每个 Markdown 文件必须包含 frontmatter：`create-time: YYYY-MM-DD` 和 `update-time: YYYY-MM-DD`
- Vue 组件导入必须带 `.vue` 扩展名
- 文件按页面归属分目录：独属于某页面的组件/样式/脚本放 `<type>/<页面名>/`，跨页面共享的放 `<type>/` 根目录
- 样式文件进一步分层：框架级样式放 `styles/base/`（global、header、footer、layout），页面级样式放 `styles/<页面名>/`
- 禁止在 Vue 文件中直接写样式，样式统一写 `.css` 文件再导入

# 风格
- 不引入不必要的抽象和过度设计

# 工作规范
- 禁止未经用户明确同意就执行 git commit
