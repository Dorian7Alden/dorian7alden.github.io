---
name: requirements-driven-development
description: 做题导向：代码依据是题目要求+测试用例，不是随意发挥
metadata:
  type: feedback
---

这是比赛做题，不是自由开发。所有代码必须服务于题目要求，符合测试用例期望。

**前置步骤**：
1. 找到题目文件（`problem/task-XX-*.md`），深度解析每条要求
2. 找到相关测试文件，理解测试的输入和期望输出
3. 以题目要求 + 测试用例为依据写代码，不自行发挥

**Why:** 之前做 Task 04 时给 Plan 加 `rows` 字段，虽然任务描述中提到了"给 Plan 节点增加统计字段"，但如果对照了题目中的 explain 输出格式和 Executor 已有的 `rows_` 统计机制，就应该能判断出 rows 应该走 Executor 而不是 Plan。最终代码是否正确，由测评说了算，不是自己觉得合理就行。

**How to apply:**
- 写代码前先把题目文件 (`problem/`) 和测试文件反复对照阅读
- 每个实现决策都要能对应到题目中的某条要求
- 不确定时优先参考测试用例的期望行为
