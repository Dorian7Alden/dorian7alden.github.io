# system-characteristics

系统的静态与动态特性记录。每个特性条目说明一个可供优化参考的事实——参数的边界值、数据结构的访问模式、资源粒度、并发模型等。

寻找性能突破点时，从这里获取目标模块的已知特性，结合特性推导浪费点。

## 结构摘要

| 条目 | 用途 |
|------|------|
| `disk_manager/` | `src/storage/disk_manager.cpp` 的特性 |
| `buffer_pool_manager/` | `src/storage/buffer_pool_manager.cpp` 的特性 — 并发模型、帧生命周期、I/O 路径 |
| `replacer/` | `src/replacer/lru_replacer.cpp` 的特性 — LRU 数据结构、内部锁、分配开销 |
| ... | 按需新增子目录 |

## 与 code-explain / performance-improve 的关系

| 目录 | 角色 |
|------|------|
| `code-explain/` | 讲解代码"为什么这么写" |
| `system-characteristics/` | 记录系统"是什么状态"（数值、边界、模式） |
| `performance-improve/` | 记录"做了什么优化" |

## 特性条目格式

无强制模板，但建议包含：值/范围、性质（静态推导/动态测试）、来源（代码位置或测试记录）、优化关联（影响什么性能决策）。
