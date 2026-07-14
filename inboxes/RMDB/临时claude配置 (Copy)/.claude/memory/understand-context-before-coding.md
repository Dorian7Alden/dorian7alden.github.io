---
name: understand-context-before-coding
description: 写代码前必须先理解完整上下文：框架架构、队友 commit、已有模式，不是一个人在开发
metadata:
  type: feedback
---

RMDB 是一个多人协作的数据库管理系统，框架已搭好。写任何代码前必须：

1. **阅读相关代码的完整上下文**，不仅是自己要改的文件，还包括上下游文件中相关的类、函数、调用链
2. **检查队友最近的 commit**（`git log`），了解他们做了什么、怎么做的，保持实现思路一致
3. **理解框架已有的模式**，在框架内行事，不自行发挥
4. **搞清楚实现的前置信息**，确认没有冲突和遗漏后再动手

**Why:** 之前做 Task 04 时，没先看队友在 `ceccf1f` 提交的 Executor 侧 explain analyze 实现（`AbstractExecutor::rows_`、`node_name()`、`children()`、`FilterExecutor`、`explain_analyze()`），就给 Plan 基类加了 `rows` 字段。如果先看了上下文，就会知道 rows 应该只在 Executor 层，Plan 加 rows 是错的。

**How to apply:** 接到任务后先不写代码，而是：
1. `git log --oneline -10` 看最近提交
2. `git show <commit>` 看队友改了什么
3. 把相关文件都读一遍（不只是自己负责的文件）
4. 理清链路后再动手
