---
name: destructive-ops-require-explicit-permission
description: 所有修改仓库、文件系统的操作必须先经用户明确同意，不得擅自执行
metadata:
  type: feedback
---

所有修改操作（git reset、git checkout、git clean、git commit、文件写入、文件删除等）在执行前必须经用户明确同意。不得因"计划已批准"或"上下文暗示"而跳过确认。

**Why:** 用户反复强调"执行的所有修改操作应该经过我的明确允许才能开始"，但 AI 仍擅自使用了 `git reset HEAD .`、`git checkout .`、`git clean -fd`，其中 `git clean -fd` 直接导致 `.TODO.md` 和 `our-test/` 永久丢失，无法恢复。

**How to apply:** 任何可能修改仓库状态、文件系统或外部系统的操作，在执行前必须向用户说明具体命令和影响，等待明确同意后再执行。即使是清理或修复操作也不例外。
