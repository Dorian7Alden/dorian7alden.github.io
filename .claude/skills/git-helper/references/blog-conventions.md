# Blog 项目 Git Commit 规范

## Commit 格式

```
type: 中文描述
```

无 scope，第一行直接描述变更意图。

## type 取值

| type | 含义 | 适用场景 |
|------|------|----------|
| `feat` | 新增功能 | 新增 Vue 组件、实现页面功能、添加交互 |
| `fix` | 缺陷修复 | 修复 bug、样式异常、逻辑错误 |
| `ref` | 重构优化 | 调整代码结构、提取公共逻辑、简化实现 |
| `style` | 样式变更 | 修改 CSS、调整布局、视觉微调 |
| `test` | 测试代码 | 新增或修改测试用例 |
| `doc` | 文档/笔记 | 更新 Markdown 文件、`_docs/`、`notes/` |
| `chore` | 构建/配置 | `package.json`、`.gitignore`、`.github/`、CI/CD 配置、删除旧文件 |

## 文件分组规则

分析改动时，按文件路径自动归组。不同组的改动必须拆成独立 commit，每组一个 commit。

| 组别 | 文件范围 | commit type |
|------|---------|:-----------:|
| 主题组件 | `.vitepress/theme/components/` | `feat` |
| 主题视图 | `.vitepress/theme/views/` | `feat` |
| 主题样式 | `.vitepress/theme/styles/`、CSS 文件 | `style` |
| 主题入口 | `.vitepress/theme/index.ts` | `feat` |
| 主题配置 | `.vitepress/config.ts` | `feat` 或 `chore` |
| 资源文件 | `.vitepress/theme/assets/`、`public/` | `feat` 或 `chore` |
| 文档 | `*.md`、`_docs/` | `doc` |
| 笔记 | `notes/` | `doc` |
| 构建配置 | `package.json`、`.gitignore`、`tsconfig.json` | `chore` |
| CI/CD | `.github/` | `chore` |
| 脚本 | `scripts/` | `chore` |
| 清理删除 | 删除旧文件/组件 | `chore` 或 `ref` |

跨组改动时，清单中列出多个 commit，按组分批执行。

## 规则提醒

- **Markdown 文件必须包含 frontmatter**：`create-time: YYYY-MM-DD` 和 `update-time: YYYY-MM-DD`
- **Vue 组件导入必须带 `.vue` 扩展名**
- 小步提交，一个逻辑改动一个 commit，不混搭
- 不引入不必要的抽象
