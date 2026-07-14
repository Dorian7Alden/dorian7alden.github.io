---
name: project-config-scope
description: 所有 Claude Code 配置（memory、settings、hooks 等）均为项目级别，存放在仓库 .claude/ 目录下，不使用用户级配置
metadata:
  type: feedback
---

所有 Claude Code 相关配置（memory、settings、hooks 等）都必须设置为项目级别，存放在当前仓库的 `.claude/` 目录下。不使用 `~/.claude/` 用户级配置。

**Why:** 用户明确要求"所有有关 claude code 的配置都设置为项目级别的，只会出现在当前的仓库内"。

**How to apply:**
1. Memory 文件写入 `.claude/memory/`，不写入 `~/.claude/projects/...`
2. Settings/Hooks 写入 `.claude/settings.json` / `.claude/settings.local.json`，不用用户级
3. 发现用户级配置时，主动迁移到项目级并清理用户级
