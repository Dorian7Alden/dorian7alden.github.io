# performance-improve

性能提升记录，以"原子笔记"形式存放。每篇围绕一次性能优化操作，记录优化对象、手段、效果。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `01-diskmanager-syscall-atomic.md` | DiskManager：lseek+write→pwrite、seq_cst→relaxed，减少系统调用和内存屏障 |
| `02-pageid-hash-optimization.md` | PageId 哈希算法优化预案（未实施）— 去冗余、改善分布、多实例分片 |
| `03-bpm-latch-granularity.md` | BufferPoolManager 锁粒度优化预案（未实施）— 将 read_page/脏页刷盘移出全局锁 |
| `04-replacer-redundant-lock.md` | LRUReplacer 内部冗余锁移除（未实施）— BPM 已持全局锁，内层锁无并发保护价值 |
| `05-fetchpage-wasted-memset.md` | fetch_page 路径上 update_page 的浪费的 memset（未实施）— reset_memory 后立即被 read_page 覆盖 |
| ... | 按序号递增 |

## 本层规则

**文件名格式：`<序号>-<主题>.md`，序号从 01 开始递增，两位数字。**
> **序号命名的原因**：便于按时间回溯和复盘，序号反映优化的先后顺序。

**每篇记录一次优化：优化前的状况 → 具体改动 → 优化效果（定性或定量）。**
> **三段式的原因**：方便复盘时快速理解每次优化的动机和成效。

**用户进行性能相关代码调整时，AI 自动将优化记录写入此目录，序号自动递增。**
> **自动沉淀的原因**：集中留存所有性能决策，方便阶段性总结和赛题提交时的性能说明。
