# RMDB

## 项目背景

RMDB 是一个关系型数据库管理系统代码框架，用于**全国大学生计算机系统能力大赛数据库管理系统赛道**。参赛队伍在此基础上设计和实现完整的数据库内核，要求具备运行 TPC-C 基准测试常用负载的能力。

项目采用[木兰宽松许可证 v2](https://license.coscl.org.cn/MulanPSL2)。

## 总目标

开发分两个场景，最终成绩由两者组成：

- **在线评测**：通过 10 道题目，满分 100 分。需要填充实现并通过所有内核模块的测试点。
- **性能评测**：通过在线性能基准测试跑分。

在线测评是通过提交指定分支来完成提交测评的。

## 项目现状

各模块基本实现完毕，10 道题的在线评测已通过。当前工作重点是 **bug 修复和性能优化**（查询优化器、执行器是近期的修改热点）。

## 开发场景

### 在线评测（10 道题）

题目的详细描述和子任务在 `docs/tasks/` 下，按编号对应一一对应。

### 性能评测

侧重于存储栈和查询引擎的效率，涉及性能分析和调优。过往的优化分析和系统特性记录在 `docs/temp-dev-doc/performance-improve/` 和 `docs/temp-dev-doc/system-characteristics/` 中。

## 目录结构

```
db2026-x/
├── src/            # 主源码，入口 rmdb.cpp:main()
├── docs/
│   ├── tasks/      # 10 道题的题目描述
│   ├── workflow/   # 工作流记录（自动测评、初赛题目、性能测试）
│   ├── official-docs/  # 官方文档（使用、环境配置、项目结构说明）
│   └── temp-dev-doc/    # 开发过程文档
├── deps/           # 依赖（googletest）
├── build/          # CMake 构建输出
├── scripts/        # 一键启动的工具脚本
├── test/           # 测试文件目录
└── CMakeLists.txt  # 项目根构建配置
```

src/ 子目录之间的依赖自底向上：common → storage/replacer → record/index → system → transaction/recovery → execution → analyze/optimizer → parser。test 为测试基础设施。

## 常用命令

```bash
# 构建（在项目根目录下）
cd build && cmake .. && make -j$(nproc)

# 构建并运行单元测试
cd build && cmake .. && make -j$(nproc) && ctest

# 构建单个目标
cd build && make rmdb        # 主程序
cd build && make unit_test   # 单元测试
```

## 要求

- CLAUDE.md 中的文件索引不要放所有文件，只需要给关键文件/文件夹进行说明就行了，每一层应该通过对应的 README.md 进行说明，渐进式披露，而不是把所有介绍都聚合到一起，低耦合。
- 所有回答内容用中文
- 目录中存在 README.md 文件时，一定要先加载 README.md 了解情况
- **禁止在未经允许的情况下合并分支**
- **禁止在未经允许的情况下合并分支**
- **禁止在未经允许的情况下合并分支**