---
name: plan-vs-executor-responsibility
description: Plan 树持有结构信息（表名、列、条件），Executor 树持有运行时统计（rows），各行其道
metadata:
  type: feedback
---

Plan 树和 Executor 树有明确分工：

- **Plan 树** — 结构信息：表名、列名、条件、is_star、tables 等。描述"做什么"。
- **Executor 树** — 运行时统计：rows_。记录"执行了多少"。

Plan 不应该有 rows 字段（Plan 不执行，不该有运行时统计）。explain analyze 输出需要同时使用两者：结构信息来自 Plan，行数来自 Executor。

**Why:** 审核中发现之前在设计文档中给 Plan 加 rows 是错误决策，经讨论纠正。

**How to apply:** 新增字段时先想清楚它属于哪个层的职责。Plan = 蓝图，Executor = 执行体。
