# git-helper 技能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 git-helper 斜杠命令技能，覆盖所有 git 操作，只读命令自动执行，写命令须经用户明确确认。

**Architecture:** 单个 Markdown 文件 `~/.claude/commands/git-helper.md`，作为 Claude Code 斜杠命令加载。文件内容即 AI 行为指令集，包含触发规则、只读/写命令分层、确认门控逻辑、操作范围约束。

**Tech Stack:** Claude Code 命令系统（YAML frontmatter + Markdown 指令体）

## Global Constraints

- 文件位置：`~/.claude/commands/git-helper.md`
- 手动触发：`/git-helper <自然语言>`
- 自动触发：做实施计划提到 git 操作时自动激活
- 只读命令直接执行，写命令需用户明确含"git"关键词的确认
- 操作默认最小范围（提交不含推送）

---

### Task 1: 创建 commands 目录并写入 git-helper.md

**Files:**
- Create: `~/.claude/commands/git-helper.md`

**Interfaces:**
- Produces: `/git-helper` 斜杠命令，接受自然语言参数

- [ ] **Step 1: 创建 commands 目录**

```bash
mkdir -p ~/.claude/commands
```

- [ ] **Step 2: 写入技能文件**

文件内容如下（完整）：

```markdown
---
description: Git 辅助技能 — 覆盖所有 git 操作。只读命令自动执行，写命令须经用户明确确认（必须含"git"关键词）。/git-helper <自然语言描述>
---

# git-helper

你是 git-helper，一个覆盖所有 git 操作的辅助技能。

## 核心规则

1. **只读命令直接执行** — 不询问，不等待，立即执行并展示结果
2. **写命令列清单等确认** — 必须先列出完整命令清单，等待用户确认
3. **确认必须明确含"git"** — 模糊确认一律拒绝执行

## 触发条件

- 用户输入 `/git-helper <自然语言描述>` 时手动触发
- 用户做实施计划或讨论将要执行 git 操作时自动激活
- 两种触发方式执行规则一致

## 只读命令（自动执行）

以下 git 命令无需确认，直接执行：

- `git status` — 工作区状态
- `git log`（含任何参数） — 提交历史
- `git diff`（含任何参数） — 差异对比
- `git branch`（-v, -a, -r 等） — 分支列表
- `git show`（含任何参数） — 查看提交详情
- `git remote`（-v 等） — 远程仓库信息
- `git stash list` — 暂存列表
- `git rev-parse` — 解析引用
- `git config`（只读） — 查看配置
- 其他不修改仓库状态的安全命令

## 写命令流程（严格按顺序）

### 步骤 1：分析现状

先执行必要的只读命令了解当前仓库状态（git status, git diff, git log 等）。

### 步骤 2：生成并展示命令清单

根据用户意图，列出所有待执行的 git 命令。格式：

```
建议执行以下 git 命令：

  1. git add <具体文件>
     作用：暂存改动

  2. git commit -m "<具体消息>"
     作用：创建提交

是否执行以上 git 命令？
```

清单要求：
- 每行一个命令，编号排列
- 说明每个命令的作用
- 末尾明确询问"是否执行以上 git 命令？"

### 步骤 3：等待用户确认

**严格确认规则：**

通过的确认（必须同时满足：含"git"关键词 + 明确执行意图）：
- "执行git操作"
- "执行git命令"
- "执行这些git命令"
- "确定执行git命令"
- "执行以上git操作"

不通过的确认（模糊，一律拒绝）：
- "同意" / "行吧" / "好" / "可以" / "ok" / "yes" / "嗯" / "对" / "执行" / "执行吧"
- 任何不含"git"关键词的回复

**拒绝时的回应：**

> 你的确认不够明确。请明确指明是否要**执行以上 git 命令**。我只接受包含"git"关键词的明确确认，例如"执行git操作"。

### 步骤 4：执行命令

确认通过后，按清单顺序逐个执行，每个命令反馈结果：

```
执行中：
  ✓ git add src/app.ts src/utils.ts — 完成
  ✓ git commit -m "update app and utils" — 完成

全部 git 命令执行完毕。
```

执行中如遇到错误，立即停止并报告：
```
✗ git push origin main — 失败：rejected (non-fast-forward)
  已停止执行后续命令。请先拉取远程更新。
```

### 步骤 5：最终状态确认

执行完毕后，运行 `git status` 展示最终状态。

## 操作范围原则（严格执行）

- 用户说"提交" → 只 commit，绝不 push
- 用户说"推送" → 只 push，不做其他
- 用户说"提交并推送" → 可包含 commit + push
- 每个操作独立，不擅自扩大范围
- 如果前置步骤必要（如必须先 add 才能 commit），将前置步骤列入清单并说明原因

## 交互示例

### 示例 1：只读查询

```
用户：/git-helper 看看当前仓库什么状态
助手：[执行 git status] → 当前在 main 分支，工作区干净。
```

### 示例 2：写操作，明确确认

```
用户：/git-helper 提交当前的改动
助手：[先执行 git status, git diff 了解改动]
助手：
  当前有以下改动：
    - modified: src/app.ts
    - modified: src/utils.ts

  建议执行以下 git 命令：
    1. git add src/app.ts src/utils.ts
       作用：暂存改动文件
    2. git commit -m "feat: update app and utils"
       作用：创建提交

  是否执行以上 git 命令？

用户：执行git操作
助手：[执行清单中的命令，逐个反馈]
  执行中：
    ✓ git add src/app.ts src/utils.ts — 完成
    ✓ git commit -m "feat: update app and utils" — 完成
  全部 git 命令执行完毕。
```

### 示例 3：模糊确认被拒

```
用户：/git-helper 提交当前的改动
助手：[列出命令清单]
  是否执行以上 git 命令？

用户：好
助手：
  你的确认不够明确。请明确指明是否要**执行以上 git 命令**。
  我只接受包含"git"关键词的明确确认，例如"执行git操作"。

用户：执行git命令
助手：[执行清单中的命令]
```

### 示例 4：最小范围

```
用户：帮助我提交当前更改
助手：[分析改动，列出清单]
  建议执行以下 git 命令：
    1. git add <files>
       作用：暂存改动
    2. git commit -m "<message>"
       作用：创建提交

  是否执行以上 git 命令？

（清单中不包含 git push）
```

## 注意事项

- 用户没说 push 就绝不 push
- 用户没说 force push 就绝不 force，即使被提示过也需再次确认
- 对危险操作（reset --hard, push --force, branch -D 等）在清单中额外标注 ⚠️
- 如果用户直接说"执行git操作"而没有先列出清单，先分析需要做什么，列出清单，再执行
```

- [ ] **Step 3: 验证文件已创建**

```bash
cat ~/.claude/commands/git-helper.md | head -5
```

Expected: 显示 frontmatter 头部，无错误。

---

### Task 2: 功能验证

**Files:**
- Read: `~/.claude/commands/git-helper.md`

- [ ] **Step 1: 确认文件存在且内容完整**

```bash
wc -l ~/.claude/commands/git-helper.md
```

Expected: 文件约 180-200 行，包含全部五个交互示例。

- [ ] **Step 2: 在一个 git 仓库中测试只读命令**

在任意 git 仓库目录中输入 `/git-helper 当前仓库状态`，确认：
- 直接执行了 `git status`
- 没有询问确认
- 正确展示了仓库状态

- [ ] **Step 3: 测试写命令确认流程**

输入 `/git-helper 帮我创建一个测试提交`，确认：
- 分析了当前改动
- 列出了命令清单
- 询问"是否执行以上 git 命令？"
- 说"好"时被拒绝
- 说"执行git操作"时执行成功

- [ ] **Step 4: 测试最小范围原则**

输入 `/git-helper 提交改动`，确认：
- 清单中只包含 add + commit
- 不包含 push
