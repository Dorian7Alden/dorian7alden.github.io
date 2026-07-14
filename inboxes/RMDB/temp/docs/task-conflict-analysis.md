# 10 道题目冲突分析报告

## 概述

本报告分析 `docs/tasks/` 下的 10 道在线评测题目之间是否存在需求冲突。通过对比各满分分支与 `main` 的实际代码差异，识别具体的合并冲突和语义冲突。

**核心结论：不存在根本性的需求冲突，10 道题目可以在一个分支中全部通过。** 但存在因为代码实现路径不同导致的**合并冲突**和**3 处语义冲突**，需要精心合并解决。

## 分支状态

| 题目编号 | 题目名称 | 满分分支 | 状态 |
|---------|---------|---------|------|
| T01 | 存储管理 | main | ✓ 已在 main |
| T02 | 查询执行 | main | ✓ 已在 main |
| T03 | 唯一索引 | task03UniqueIndex | ✓ 已合并到 main |
| T04 | 查询优化 | task04QueryOptimization-β | ✗ 待合并 |
| T05 | 聚合函数 | main | ✓ 已在 main |
| T06 | Union 集合算子 | main | ✓ 已在 main |
| T07 | 嵌套循环连接 | task07Join-β | ✓ 已合并到 main |
| T08 | 事务控制 | task08Transaction | ✓ 已合并到 main |
| T09 | 隔离级别 | task09Isolation-Ω | ✗ 待合并 |
| T10 | 故障恢复 | taskPerformance | ✗ 待合并 |

需要合并的分支只有 3 个：**T04、T09、T10**。

## 依赖图

```
T01 ──→ T02 ──→ T03 ──→ T06
                │         ↗
                ├─→ T05 ─┘
                │
                ├─→ T04
                │
                ├─→ T07
                │
                └─→ T08 ──→ T09 ──→ T10
```

## 合并冲突矩阵

### 文件级别冲突

**三个分支全部修改的文件（7 个）— 最高风险**：

| 文件 | T04 改动 | T09 改动 | T10 改动 |
|------|---------|---------|---------|
| `src/analyze/analyze.cpp` | 别名系统、display_str、兼容类型 | SET TRANSACTION 解析 | LOAD 解析等 |
| `src/common/common.h` | Value.raw_str, TabCol.alias, Condition.display_str | 数据结构扩展 | 类型定义扩展 |
| `src/execution/execution_common.h` | condition_to_string | ReconstructTuple 重写, GetVisibleRecord 重写 | 函数接口适配 |
| `src/parser/ast.h` | AST 节点扩展 | SetTransactionIsolation AST | Load AST |
| `src/parser/lex.l` | 词法扩展 | SET TRANSACTION 关键字 | LOAD 关键字 |
| `src/parser/lex.yy.cpp` | flex 生成的词法器 | 同上 | 同上 |
| `src/parser/yacc.y` | 语法规则扩展 | SET TRANSACTION 语法 | LOAD 语法 |

**两个分支共同修改的文件（7 个）**：

| 文件 | 涉及分支 | 冲突性质 |
|------|---------|---------|
| `src/optimizer/planner.cpp` | T04, T10 | T04 重写 make_one_rel, T10 小幅修改 |
| `src/execution/execution_manager.cpp` | T04, T10 | T04 改 EXPLAIN 输出, T10 性能优化 |
| `src/transaction/transaction_manager.cpp` | T09, T10 | T09 修 MVCC abort, T10 改 abort+commit |
| `src/execution/executor_insert.h` | T09, T10 | 功能相似但实现路径不同，代码重排 |
| `src/execution/executor_update.h` | T09, T10 | T09 加自引用更新, T10 优化 |
| `src/execution/executor_index_scan.h` | T09, T10 | T09 加 MVCC 感知扫描, T10 优化 |
| `src/rmdb.cpp` | T09, T10 | T09 改主循环, T10 加 checkpoint/load |

### 语义冲突分析

#### 冲突 1：T04 强制 SeqScan vs T07 INLJ 的 IndexScan ⚠️ 高优先级

**风险等级：高**

T04 分支在 `make_one_rel()` 中强制使用 SeqScan：
```cpp
// T04 planner.cpp line 418-421
// 题目要求仅使用 SeqScan，不使用索引扫描
index_col_names.clear();
std::shared_ptr<Plan> scan_plan =
    std::make_shared<ScanPlan>(T_SeqScan, sm_manager_, tab_name, curr_conds, index_col_names);
```

而 T07（已合入 main）在 `make_one_rel()` 后有 INLJ 重写逻辑，将符合条件的 SeqScan 节点改为 IndexScan：
```cpp
// main planner.cpp line 410-415
if (can_use_inlj) {
    // INLJ: 更新右侧 ScanPlan 标签为 IndexScan
    sp->tag = T_IndexScan;
    sp->index_col_names_ = {inlj_index_col};
}
```

**分析**：

- T04 的题目描述中"本题只要求顺序扫描，type 固定为 SeqScan"的含义是：**T04 的测试用例不创建索引**，所以 EXPLAIN ANALYZE 输出中自然不会有 IndexScan
- T04 分支中**仍然保留了**单表查询的 IndexScan 逻辑（`make_scan_executor` 中的 `get_index_cols` + `T_IndexScan`），只是在多表查询的 `make_one_rel` 中强制 SeqScan
- T04 的 `make_one_rel` 整体重写幅度大，没有包含 T07 的 INLJ 逻辑

**结论：不是根本性需求冲突，是合并时的代码缺失。** 合并策略：以 main（含 T07 INLJ 逻辑）的 `make_one_rel` 为骨架，叠加 T04 的别名感知改造。T04 的 SeqScan 强制策略保留在基础扫描计划中即可（INLJ 逻辑会在后续独立地将 Scan tag 改为 IndexScan）。

#### 冲突 2：T09 与 T10 的 MVCC abort/commit 实现 ⚠️ 高优先级

**风险等级：高**

T09 修改了 MVCC 模式下的事务 abort 逻辑：
```cpp
// T09 transaction_manager.cpp
case WType::DELETE_TUPLE:
{
    // MVCC 逻辑删除：abort 回滚版本链后不能再物理恢复
    if (concurrency_mode_ == ConcurrencyMode::MVCC) {
        break;  // 跳过物理恢复
    }
    // ... 物理恢复旧记录
}
```

T10 也做了类似的修改，但实现方式略有不同——T10 在 abort 时创建了临时 Context 对象来正确判断 MVCC 模式。

**分析**：两个分支的修改目标一致（MVCC 下 DELETE 的 abort 不应物理恢复），但实现路径不同。T10 的版本更完善（使用 Context 传递 MVCC 模式），但也更复杂。

**结论：功能等价冲突，需要选择最完整的实现。** 建议以 T10 的实现为基础，融入 T09 的版本链清理逻辑。

#### 冲突 3：三个分支全部修改 execution_common.h ⚠️ 高优先级

**风险等级：高**

- T04 添加了 `condition_to_string()` 和 `compare_typed_value()` 辅助函数，以及 INT+FLOAT 兼容类型处理
- T09 重写了 `ReconstructTuple()`（支持 UPDATE 的 modified_fields、DELETE 标记）和 `GetVisibleRecord()`（修正 in_progress 跳过逻辑）
- T10 可能进一步调整这些函数

**分析**：这三个改动虽然在同一文件中但作用在不同区域。T04 的改动是增量添加，T09 和 T10 的改动在 MVCC 可见性函数上有重叠。

**结论：需要逐函数合并。** `condition_to_string` 等 T04 新增的函数可直接保留。`ReconstructTuple` 和 `GetVisibleRecord` 需要对比 T09 和 T10 的版本，选择逻辑最完整的实现。从代码分析来看 T09 的 `GetVisibleRecord` 修正更彻底（基于 writer_id 成段跳过 in_progress 链），T10 在此基础上应该保持一致。

#### 冲突 4：Parser 文件三向合并

**风险等级：中**

三个分支都需要修改解析器：
- T04：AST 节点扩展（TabCol.alias 等）
- T09：新增 `SET TRANSACTION ISOLATION LEVEL` 语法
- T10：新增 `LOAD` 语法

**分析**：这些是语法规则的独立扩展，理论上可以线性合并。但 `lex.yy.cpp` 和 `yacc.tab.cpp` 是自动生成的文件，冲突时需要重新生成。

**结论：需要按顺序合并后重新生成 parser。** 合并顺序：先 T04 的 AST 扩展，再 T09 的语法规则，最后 T10 的语法规则。

#### 冲突 5：T09 与 T10 的 executor_insert/update 差异

**风险等级：中**

两个分支都修改了 `executor_insert.h` 和 `executor_update.h`：

- T09：重排了操作顺序（版本链→WAL→索引→SSI），新增 `CheckLogicalKeyWriteConflict`
- T10：也调整了操作顺序，新增了 DML target 去重/排序（在 portal.h 而非 executor 中）

**分析**：两个分支的操作顺序都正确——MVCC 版本链必须在 WAL 之前更新，索引维护可以在 WAL 之后。T09 的 `CheckLogicalKeyWriteConflict` 是独立功能，T10 没有。需要确认两者的操作顺序是否完全一致。

**结论：功能增量的叠加合并。** 以 T09 的操作为基础，叠加 T10 的性能优化（去重、排序），确保操作顺序一致。

## 合并策略建议

### 推荐合并顺序

```
T04（查询优化）→ T09（隔离级别）→ T10（故障恢复+性能）
```

**理由**：

1. T04 改动在查询计划层，T09 改动在事务/执行层，耦合最弱，先合并 T04 影响面可控
2. T09 的 MVCC 修改是 T10 恢复机制的前置依赖（恢复依赖 MVCC 可见性函数）
3. T10 改动量最大（+5298/-2801），最后合并可减少反复解决冲突的工作量

### 各阶段关键操作

**阶段 1：合并 T04**

| 文件 | 策略 |
|------|------|
| `analyze.cpp` | 保留 main 的已有逻辑，叠加 T04 的 alias/display_str/兼容类型 |
| `common.h` | 合并 T04 的 Value.raw_str, TabCol.alias, Condition.display_str |
| `planner.cpp` | **重点**：保留 main 的 INLJ 逻辑，叠加 T04 的别名感知改造和 Project 下推完善 |
| `execution_common.h` | 添加 T04 的 condition_to_string/compare_typed_value，不影响已有函数 |
| `parser/*` | 合并 T04 的 AST 扩展 |

**阶段 2：合并 T09**

| 文件 | 策略 |
|------|------|
| `execution_common.h` | 用 T09 版本替换 ReconstructTuple 和 GetVisibleRecord（MVCC 修正） |
| `transaction_manager.cpp` | 合并 T09 的 MVCC abort 修正 |
| `executor_insert.h` | 合并 T09 的 CheckLogicalKeyWriteConflict 和操作顺序 |
| `executor_update.h` | 合并 T09 的自引用更新支持 |
| `executor_index_scan.h` | 合并 T09 的 MVCC 感知扫描 |
| `parser/*` | 添加 T09 的 SET TRANSACTION 语法 |
| `rmdb.cpp` | 合并 T09 的主循环重构 |

**阶段 3：合并 T10**

| 文件 | 策略 |
|------|------|
| `execution_common.h` | 保持 T09 版本的 MVCC 函数，叠加 T10 的接口适配（如有不一致） |
| `transaction_manager.cpp` | 以 T09 的语义为基础，合并 T10 的 Context 改进和清理 |
| `log_manager.cpp/h` | 完整采用 T10 的实现 |
| `log_recovery.cpp/h` | 完整采用 T10 的实现 |
| `executor*.h` | 叠加 T10 的性能优化 |
| `CMakeLists.txt` | 采用 T10 的 -O2 |
| `portal.h` | 合并 T10 的 LoadPlan/DML 排序去重 |
| `parser/*` | 添加 T10 的 LOAD 语法 |

### 验证清单

每个合并阶段完成后，运行以下验证：

**阶段 1 完成后（T04）**：
1. 运行 T01~T03 单元测试，确认无回归
2. 运行 T04 EXPLAIN ANALYZE 测试，确认计划树正确
3. 运行 T05~T07 测试，确认查询执行无回归

**阶段 2 完成后（T09）**：
4. 运行 T08 事务测试，确认单线程事务无回归
5. 运行 T09 SI/SER 测试，确认写写冲突、快照隔离、SSI 正确
6. 回跑 T04 EXPLAIN ANALYZE 测试

**阶段 3 完成后（T10）**：
7. 运行 T10 故障恢复测试，确认恢复后数据一致性
8. 运行 T09 SI/SER 测试，确认恢复后 MVCC 可见性规则保持
9. 运行全量测试，确认 T01~T10 全部通过

## 冲突矩阵

```
      T01  T02  T03  T04  T05  T06  T07  T08  T09  T10
T01    -    ✓    ✓    ✓    ✓    ✓    ✓    ✓    ✓    ✓
T02    ✓    -    ✓    ✓    ✓    ✓    ✓    ✓    ✓    ✓
T03    ✓    ✓    -    ○    ○    ✓    ✓    ✓    ○    ○
T04    ✓    ✓    ○    -    ○    ○    ●    ○    △    △
T05    ✓    ✓    ○    ○    -    ○    ○    ○    ○    ○
T06    ✓    ✓    ✓    ○    ○    -    ○    ○    ○    ○
T07    ✓    ✓    ✓    ●    ○    ○    -    ○    ○    ○
T08    ✓    ✓    ✓    ○    ○    ○    ○    -    ✓    ✓
T09    ✓    ✓    ○    △    ○    ○    ○    ✓    -    ●
T10    ✓    ✓    ○    △    ○    ○    ○    ✓    ●    -

图例：
✓  兼容：已合并或无冲突
○  并行独立：实现互不干扰
△  文件级冲突：修改同一文件，但改动在不同区域，可线性合并
●  语义级冲突：修改同一逻辑区域，需要仔细合并并验证
```

## 总结

10 道题目的需求本身不存在冲突——每个题目都在前置题目基础上做增量扩展，不要求修改已有行为。实际冲突全部来自**同一文件被多个分支以不同方式修改**导致的合并冲突。

| 冲突类型 | 数量 | 处理方式 |
|---------|------|---------|
| 文件级（同一文件不同区域） | 10 个文件 | 线性合并，无歧义 |
| 语义级（同一逻辑区域） | 3 处 | 需对比选择最优实现或组合 |
| Parser 生成文件 | 2 个文件 | 合并规则后重新生成 |

**3 个语义冲突**的合并决策已在上述"合并策略"中给出。核心原则是：**以 main 为骨架，保留每个分支的独特功能，对重叠区域选择逻辑最完整的版本。**
