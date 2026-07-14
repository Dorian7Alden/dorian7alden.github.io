---
name: git-helper
description: Git 辅助技能，覆盖所有 git 操作。只读命令自动执行，写命令须经用户确认（必须含"git"关键词）。当用户讨论 git 操作、提交、分支、合并、推送、rebase、stash、或输入 /git-helper 时触发。即使对话中只是顺带提到"提交一下"、"帮我看看分支"等也应激活。
---

# git-helper

## 核心规则

1. **只读命令直接执行** — 不询问，立即执行并展示结果
2. **写命令列清单等确认** — 先列出完整命令清单，等待用户确认
3. **确认必须含"git"** — 模糊确认一律拒绝。通过的确认："执行git操作"、"执行git命令"等含"git"关键词的明确表述。拒绝的确认："好"、"可以"、"行"、"ok"、"yes"、"执行"等
4. **严格按用户指令操作** — 用户说"提交"只 commit 不 push；说"推送"只 push；说"提交并推送"才可 commit+push。每个操作独立，不擅自扩大范围。前置步骤（如 add 才能 commit）列入清单并说明原因
5. **危险操作额外标注** — 对 `reset --hard`、`push --force`、`branch -D` 等危险命令在清单中额外标注 ⚠️。用户没说 force push 就绝不 force，即使被提示过也需再次确认。

## 触发条件

- 用户输入 `/git-helper <描述>` 时手动触发
- 用户讨论或将要执行 git 操作时自动激活（提到提交、分支、合并、推送、rebase、stash 等）
- 两种触发方式执行规则一致

## 只读命令

`git status`、`log`、`diff`、`branch`、`show`、`remote`、`stash list`、`rev-parse`、`config --list` 等不修改仓库状态的命令，直接执行不确认。

## 写命令流程

### 步骤 1：分析现状

执行必要的只读命令了解当前仓库状态。

### 步骤 2：分析改动并生成分组命令清单

根据文件路径按组拆分 commit。分组规则、type 取值、scope 映射（题号 `t01`-`t10` / 模块名）及上下文推断规则，全部参见 `references/rmdb-conventions.md`。

清单格式：

```
建议执行以下 git 命令：

  【第 1 组：源码 — feat(t01)】
  1. git add src/storage/buffer_pool_manager.cpp
     作用：暂存源码改动
  2. git commit -m "feat(t01): 实现 BufferPool 页面管理"
     作用：创建源码提交

  【第 2 组：配置 — chore(config)】
  3. git add .gitignore
     作用：暂存配置改动
  4. git commit -m "chore(config): 更新 .gitignore 忽略规则"
     作用：创建配置提交

是否执行以上 git 命令？
```

### 步骤 3：等待用户确认

确认必须含"git"关键词。模糊确认一律拒绝，回应：

> 你的确认不够明确。请明确指明是否要**执行以上 git 命令**。我只接受包含"git"关键词的明确确认，例如"执行git操作"。

如果用户直接说"执行git操作"而没有先列出清单，先分析需要做什么，列出清单，再执行。

### 步骤 4：执行命令

按清单顺序逐个执行，反馈结果：

```
执行中：
  ✓ git add src/app.ts — 完成
  ✓ git commit -m "..." — 完成

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
助手：[分析现状，发现 src/execution/ 和 .gitignore 两组改动]

  建议执行以下 git 命令：

  【第 1 组：源码】
  1. git add src/execution/seq_scan.cpp
     作用：暂存源码改动
  2. git commit -m "feat(t02): 实现顺序扫描算子"
     作用：创建源码提交

  【第 2 组：配置】
  3. git add .gitignore
     作用：暂存配置改动
  4. git commit -m "chore(config): 更新忽略规则"
     作用：创建配置提交

  是否执行以上 git 命令？

用户：执行git命令
助手：[按序执行，逐个反馈，最后 git status]
```

## RMDB 项目 Git 协作规范

项目专有的 commit 规范、分支策略、禁止事项见 `references/rmdb-conventions.md`。
