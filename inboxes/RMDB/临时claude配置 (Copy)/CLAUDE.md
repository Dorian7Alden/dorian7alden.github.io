# CLAUDE.md

**本文件只放任务调度和顶层工作范式，不放细节。细节通过文件加载，下文说明各文件何时加载。**

**本文件中每条规则必须同时说明「规则本身」和「原因」。规则本身用正文，原因用 `>` 引用块标注，格式为 `> **<标题>的原因**：<具体原因>`。原因是用户偏好或要解决的问题，作为未来调整规则时的决策依据，防止规则冲突时无法判断优先级。**

**AI 不得自行执行 git add / commit / push 等修改仓库的操作，必须经用户明确同意。默认做法是指导用户怎么做，让用户自己完成。**

**用户询问 git 操作时，使用 `git-assistant` skill，不要只凭自己记忆回答。**

## 启动时

加载项目本地记忆：读取 `.claude/memory/MEMORY.md` 及其索引的所有记忆文件。此目录在项目仓库内，不在系统提示的 `~/.claude/projects/` 路径下。

## 构建与测试

```bash
cd build && cmake .. && make -j$(nproc)
cd build && make unit_test && ./bin/unit_test
cd build && ./bin/unit_test --gtest_filter="SuiteName.*"
cd build && ./bin/rmdb <database_name>
```

## 架构

入口 `src/rmdb.cpp:main()`。流水线 `Parser → Analyze → Optimizer/Planner → Portal → Execution`。存储栈 `DiskManager → BufferPoolManager(LRUReplacer) → Record/Index → Transaction → Recovery`。依赖自底向上。

## .cpp 函数排序规则

**实现文件中，函数按调用层次从顶向下排列：先顶层函数（调用方），后底层函数（被调用方）。** 读者应先看到模块做了什么（职责边界），再看到怎么做的（内部细节）。
> **顶层优先的原因**：底层函数先出现时，读者没有上下文，不知道它被谁调用、为什么存在、入参从哪来，只能硬读实现细节。`update_page` 就是个教训——它出现在 `find_victim_page` 之后、`fetch_page` 之前，但它的职责边界只有结合调用方（`fetch_page` / `new_page`）才能理解。

**如果发现顺序不对（底层函数排在调用它的顶层函数之前），执行调整。**
> **执行调整的原因**：顺序混乱的代码每读一次都浪费一次理解成本。长痛不如短痛，看到就修。

## 函数 doxygen 注释规范

**读取或编写函数时，检查 @description 是否覆盖三层信息：(1) 函数的作用——它做了什么，(2) 处理效果——做了哪些处理、达到什么结果，(3) 职责边界——不做什么、调用方需要负责什么。缺层或描述模糊的立即修正。**
> **三层描述的原因**：`update_page` 原描述"更新页面数据"让人以为它加载了新数据，实际它不加载、数据由调用方负责；`new_page` 的描述没说 fd 需调用方预置。不说明职责边界的注释需要读者翻上下文确认，失去注释的存在意义。

## README 分层摘要规则

**每个目录下必须有 README.md。** README.md 只描述当前目录自身的内容，不涉及父目录，也不涉及子目录。作用范围严格限制在当前目录内。
> **分层摘要的原因**：避免每次进入一个目录都需要全量读取文件来理解结构，用 README.md 作为该层的索引，按需加载。

**例外：项目根目录的 README.md 不适用此规则。** 根目录 README.md 是项目的对外门面，面向外部访问者，不按内部结构摘要的格式编写。根目录的结构摘要和顶层规则由 CLAUDE.md 承载。
> **根目录例外的原因**：根目录 README.md 是 GitHub/仓库首页展示用，受众是外部用户；CLAUDE.md 是内部工作用的索引和规则集。两者定位不同，不应混淆。

README.md 包含两部分：
1. **结构摘要**：当前目录的作用，目录下每个文件和子目录（仅列出名称）的作用。
2. **本层规则**：当前目录下内容的特殊处理约定，如文件命名规则、文件只用来做什么、不得做什么等。每条规则必须同时给出原因，格式为 `> **<标题>的原因**：<具体原因>`，便于未来调整时理解当初的决策背景。
> **规则与结构同处一处的原因**：规则是目录内容的一部分约束，放在 README.md 中随目录走，发现成本最低。每个目录的规则作用范围仅限于该目录，防止不同目录的规则相互干扰，避免规则冲突时无法判断优先级。

**加载策略**：先读 README.md 获取结构摘要，再决定需要读哪些具体文件。不要每次直接全量读取所有文件来理解内容。
> **先读摘要再按需加载的原因**：减少全量读取带来的 token 消耗和噪音，让 AI 和开发者都能快速定位目标文件。

**创建新目录或增删文件时，必须同步更新该目录的 README.md。**
> **同步更新的原因**：README.md 是结构摘要，内容变更后摘要必须同步，否则索引失效，后续读者会被过期信息误导。

**新建文件前，必须先读取目标目录的 README.md，确认该目录的作用和规则，判断文件放在这里是否正确。**
> **新建前先读 README 的原因**：防止文件归错目录。本次踩过坑：BufferPoolManager 的讲解文档被错误放入 `page/` 目录，因为没读 README 确认目录定位。先读 README 的"结构摘要"和"本层规则"，验证目标目录的职责范围是否匹配要创建的文件，避免分类混乱。

## 关键文件

| 文件 | 何时加载 |
|------|----------|
| `.claude/memory/MEMORY.md` | 启动时 |
| `.claude/memory/user-profile.md` | 启动时（用户偏好） |
| `.claude/memory/comment-style.md` | 编写或修改代码时 |
| `.claude/memory/no-source-modification-in-tests.md` | 编写测试时（优先读取） |
| `.claude/skills/rmdb-implementation/SKILL.md` | 实现函数接口时（自动触发） |
| `.claude/skills/rmdb-test-writing/SKILL.md` | 编写测试时（自动触发） |
| `.claude/skills/git-assistant/SKILL.md` | 用户询问 git 操作时（自动触发） |
| `.claude/skills/rmdb-performance-improve/SKILL.md` | 性能优化时（自动触发）— 完整 6 步流程：识别→分析→验证→对比→改码→文档 |
| `.claude/skills/conversation-to-docs/SKILL.md` | 用户针对源代码提问并得到解答后（自动触发），将问答整理到 dev-doc/code-explain/；用户要求整理/维护文档时（手动触发） |
| `.claude/skills/rmdb-code-annotate/SKILL.md` | 给指定函数体写注释时（自动触发）— 按逻辑块分组，一行中文注释，只描述动作 |
| `.claude/memory/project-config-scope.md` | 修改 Claude Code 配置时 |
| `.claude/memory/mermaid-gitgraph-rules.md` | 编写或修改 mermaid gitGraph 时 |
| `probHTML2MD/output/task-<编号>-*.md` | 开始做某道赛题时；首次需运行 `probHTML2MD/run.sh` 生成 |
| `doc/RMDB项目结构.md` | 需要了解模块细节时 |
| `doc/RMDB使用文档.md` | 编译/运行遇到问题时 |
| `doc/RMDB环境配置文档.md` | 环境配置遇到问题时 |
| `doc/测试说明文档2026.md` | 编写测试参考时 |
| `src/unit_test.cpp` | 添加或运行测试时 |
| `our-test/` | 编写自定义测试时 |
| `src/errors.h` | 处理异常时 |

## 源码问答后自动文档

**检测到用户对 src/ 下源码的提问时，必须先 invoke conversation-to-docs skill 加载其流程，再在回答时同步完成文档产出。将文档产出视为回答的一部分，而非回答后的额外步骤。**
> **先 invoke 再回答的原因**：三次踩坑——`update_page`、`scoped_lock`、`new_page` 的问答都是用户手动提醒后才补文档。如果先回答再想起来补，必然漏。invoke skill 的动作必须前置到回答之前。

