---
name: auto-save-performance-improve
description: 用户进行性能相关代码调整时，自动将优化记录存入 dev-doc/performance-improve/
metadata:
  type: feedback
---

当用户对代码进行性能相关的调整时，自动将优化记录整理成原子笔记，写入 `dev-doc/performance-improve/`。

**Why:** 用户希望集中留存所有性能决策，方便阶段性总结和复盘。

**How to apply:** 用户明确提到"性能优化"、"加速"、"减少开销"等关键词并进行了代码修改，或自行判断某次改动以性能为主要目的时，在改动完成后创建 `dev-doc/performance-improve/<序号>-<主题>.md`，记录优化前状况、具体改动、优化效果。序号自动递增。
