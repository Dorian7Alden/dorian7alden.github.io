---
name: rmdb-performance-improve
description: RMDB 项目性能优化专用技能。当用户讨论性能相关问题、提出优化想法或尝试、分析某个模块的性能改进空间、或说"优化"、"提速"、"减少开销"、"找性能突破点"等关键词时触发。适用范围不限于代码修改——性能分析、方案探讨、调参实验、瓶颈定位等都在范围内。
---

# RMDB 性能优化

协助完成性能相关的分析、验证与文档沉淀。

## 当前阶段

**理论分析阶段**。重点工作是熟读源码 + 文档记录，不急于实现。本地测试框架尚未建立——这是后续步骤（验证、对比、改码）的前置依赖，待框架就绪后再推进到实现阶段。

> **测试框架缺失的影响**：目前无法跑可重复的基准负载来获取 profiling 数据，也无法在改动后做 A/B 对比。当前产出以「静态分析 + 理论推导」为主，标注为"待实测验证"。测试框架到位后，这些标注项将成为假设驱动闭环的起点。

## 核心原则

- **先读代码，再谈优化**：对模块的实现细节有精确认知后再分析性能。凭"教科书上说 XX 是这样做的"去推断会踩坑——RMDB 的实现细节和 PostgreSQL/InnoDB 差很多。
- **测量先行，不凭直觉**：数据库内核性能高度反直觉——直觉只能跨越 2-3 层抽象，而一个 OLTP 请求从 SQL 到磁盘要经过 15+ 层。有测试框架后用 perf/火焰图/iostat 量化瓶颈。（当前阶段以静态分析替代，明确标注"待实测"。）
- **聚焦关键路径**：阿姆达尔定律——不在关键路径上的优化是无效优化。TPC-C 中 New-Order + Payment 占 88% 事务量。
- **利用系统中已有的特性去省开销**：pwrite 替代 lseek+write、relaxed 内存序替代 seq_cst。
- **方案参考已知最佳实践**：不凭空猜测。参考 PostgreSQL/InnoDB/RocksDB/DuckDB 的成熟设计。
- **改动前必须通过 subAgent（isolation: worktree）编译 + 全量测试**（测试框架就绪后启用）。
- **改动后必须更新对应文档**。

## 优化流程（6 步闭环）

当前可执行：① ② ⑥。③④⑤ 待测试框架就绪。

1. **识别**：读代码 + 维度扫描 → 定位潜在瓶颈。有 profiling 数据后补充火焰图/syscall 统计交叉验证
2. **分析**：提取目标模块的精确特性（值范围、访问模式、并发模型），找到浪费点，记录到 `system-characteristics/`
3. **验证**：subAgent（isolation: worktree）编译 + 全量测试（**待测试框架**）
4. **对比**：改动前后跑相同负载，记录定量数据（**待测试框架**）
5. **改码**：落地最小可行变更（**待前两步就绪**）
6. **文档**：更新 system-characteristics / code-explain / performance-improve（**当前主要产出**）

## 方法论

参见 `references/methodology-index.md`——一个可积累的方法论库。

| 方法 | 文件 | 适合场景 |
|------|------|----------|
| 特征驱动 | `characteristics-driven.md` | 从代码特性出发，系统性地找可省的开销 |
| 假设驱动 | `hypothesis-driven.md` | 有 profiling 数据，形成假设→验证的闭环 |
| 维度扫描 | `dimensional-scanning.md` | 需要灵感启发，按预定义清单逐一排查 |

三种方法不互斥：可先用维度扫描或特征驱动找到候选方向，再用假设驱动验证。

通用理论见 `references/optimization-theory.md`，RMDB 专项参考见 `references/rmdb-optimization-scope.md`。

## RMDB 常见性能债

教学框架为可读性做的性能牺牲，是优化的起点：

1. **粗粒度锁**：全局 buffer pool mutex、全局 lock manager latch、WAL 写入全局锁
2. **低效替换算法**：纯 LRU 无 midpoint insertion，全表扫描会污染热数据
3. **WAL 串行化**：每次 commit 独立 fsync，无 group commit
4. **B+Tree 读写放大**：节点未压缩、分裂/合并全锁、范围扫描无 prefetch
5. **查询执行低效**：火山模型逐行 next()（虚函数调用开销）、无 plan cache
6. **I/O 路径陈旧**：同步阻塞 read/write、lseek+write 分离调用
7. **内存管理粗糙**：标准 new/delete，无内存池

## 文档产出

所有性能相关产出归入 `dev-doc/` 的三个子目录：

- `system-characteristics/` — 系统特性记录（供后续分析参考）
- `code-explain/` — 技术点讲解（按源文件分类）
- `performance-improve/` — 优化记录（前后对比 + 收益分析）
