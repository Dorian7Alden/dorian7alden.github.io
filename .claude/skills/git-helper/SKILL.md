---
name: git-helper
description: Git 辅助技能，覆盖所有 git 操作。只读命令自动执行，写命令列清单等用户确认。当用户提及"提交"、"推送"、"分支"、"合并"、"rebase"、"stash"等 git 操作时自动激活。
---

# git-helper

## 核心规则

1. **只读命令直接执行** — 不询问，立即执行并展示结果
2. **写命令列清单等确认** — 先列出完整命令清单，等待用户确认
3. **严格按用户指令操作** — 用户说"提交"只 commit 不 push；说"推送"只 push；说"提交并推送"才可 commit+push。每个操作独立，不擅自扩大范围。前置步骤（如 add 才能 commit）列入清单并说明原因
4. **危险操作额外标注** — 对 `reset --hard`、`push --force`、`branch -D` 等危险命令在清单中额外标注 ⚠️。用户没说 force push 就绝不 force，即使被提示过也需再次确认。

## 触发条件

- 用户输入 `/git-helper <描述>` 时手动触发
- 用户讨论或将要执行 git 操作时自动激活（提到提交、分支、合并、推送、rebase、stash 等）

## 只读命令

`git status`、`log`、`diff`、`branch`、`show`、`remote`、`stash list`、`rev-parse`、`config --list` 等不修改仓库状态的命令，直接执行不确认。

## 写命令流程

### 步骤 1：分析现状

执行必要的只读命令了解当前仓库状态（`git status`、`git diff --stat`、`git log --oneline -10`）。

### 步骤 2：分析改动并生成分组命令清单

根据文件路径按组拆分 commit。分组规则、type 取值参见 `references/blog-conventions.md`。

清单格式：

```
待执行的 git 命令：

  【第 1 组：主题/组件 — feat】
  1. git add .vitepress/theme/components/NewComponent.vue
     作用：暂存新组件
  2. git commit -m "feat: 新增某组件"
     作用：创建组件提交

  【第 2 组：配置 — chore】
  3. git add .gitignore
     作用：暂存配置改动
  4. git commit -m "chore: 更新 .gitignore 忽略规则"
     作用：创建配置提交

确认执行？
```

### 步骤 3：等待用户确认

列出清单后等待用户确认，确认后按序执行。

### 步骤 4：执行命令

按清单顺序逐个执行，反馈结果：

```
执行中：
  ✓ git add .vitepress/theme/components/NewComponent.vue — 完成
  ✓ git commit -m "feat: 新增某组件" — 完成

全部 git 命令执行完毕。
```

遇到错误立即停止并报告：

```
✗ git push origin main — 失败：rejected (non-fast-forward)
  已停止执行后续命令。请先拉取远程更新。
```

### 步骤 5：最终状态确认

执行 `git status` 展示最终状态。

## 交互示例

```
用户：提交当前的改动
助手：[分析现状，发现 .vitepress/theme/ 和 .gitignore 两组改动]

  待执行的 git 命令：

  【第 1 组：主题 — feat】
  1. git add .vitepress/theme/components/Header.vue
     作用：暂存新组件
  2. git commit -m "feat: 新增 Header 组件"
     作用：创建提交

  【第 2 组：配置 — chore】
  3. git add .gitignore
     作用：暂存配置改动
  4. git commit -m "chore: 更新 .gitignore 忽略规则"
     作用：创建提交

  确认执行？

用户：执行
助手：[按序执行，逐个反馈，最后 git status]
```
