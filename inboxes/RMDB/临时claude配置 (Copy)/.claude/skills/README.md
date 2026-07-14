# .claude/skills

Claude Code 自定义技能（skill）目录。每个子目录定义一个技能，通过 `/技能名` 触发。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `conversation-to-docs/` | 会话讨论转结构化文档 |
| `git-assistant/` | Git 操作指导与协作规则 |
| `rmdb-implementation/` | RMDB 函数/方法的标准化实现流程 |
| `rmdb-test-writing/` | RMDB 测试编写的标准化流程 |

## 本层规则

**每个 skill 目录下必须有 SKILL.md 作为入口。**
> **统一入口的原因**：Claude Code 按约定查找 SKILL.md，统一命名确保框架能正确发现和加载技能。
