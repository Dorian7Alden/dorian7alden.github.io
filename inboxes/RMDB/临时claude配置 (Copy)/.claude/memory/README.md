# .claude/memory

项目本地记忆文件，AI 启动时加载，用于跨会话持久化信息。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `MEMORY.md` | 记忆索引，指向本目录下所有记忆文件 |
| `user-profile.md` | 用户身份、偏好与工作方式 |
| `comment-style.md` | 注释规范：中文注释、每声明必注释 |
| `no-source-modification-in-tests.md` | 写测试时不得修改 src/ 的规则 |
| `project-config-scope.md` | 配置作用域规则：全部用项目级配置 |
| `mermaid-gitgraph-rules.md` | Mermaid gitGraph 中 commit id 必须唯一 |
| `dont-delete-comments.md` | 不得随意删除已有注释 |
| `understand-context-before-coding.md` | 写代码前先理解上下文、队友提交和已有模式 |
| `requirements-driven-development.md` | 做题导向：代码依据是题目要求和测试用例 |
| `critical-thinking.md` | 批判性思维审核一切建议 |
| `plan-vs-executor-responsibility.md` | Plan 树与 Executor 树的职责分离 |
| `feedback-destructive-operations.md` | 修改仓库/文件系统的操作须用户明确同意 |
| `feedback-merge-conflicts.md` | 合并冲突须由用户决定取舍 |
| `feedback-wait-for-explicit-yes.md` | 提问后须等待明确肯定答复 |

## 本层规则

**记忆文件命名使用 kebab-case，用 `.md` 后缀。**
> **命名规则的原因**：kebab-case 与文件系统的 slug 语义一致，MEMORY.md 中的链接可直接引用。

**每个记忆文件必须有 frontmatter（name、description、metadata）。**
> **frontmatter 的原因**：提供结构化元数据，便于 MEMORY.md 索引和 AI 按需加载。

**记忆内容只放跨会话有效的信息，不放当前会话的临时状态。**
> **时效性的原因**：避免过期信息污染上下文，临时的任务进度用 Task 系统管理。
