---
name: rmdb-test-writing
description: 为 RMDB 模块编写测试时触发。当用户说要写测试、加测试、给某个模块补测试、新建测试文件时使用。提供从代码理解到可运行测试套件的完整 7 步流程，确保测试文件符合项目编号规范、中文输出规范和 CMake 集成规范。
---

# RMDB 测试编写

为 RMDB 项目模块编写测试代码的标准流程。每个步骤必须按顺序执行，不可跳过。

这些所有步骤是一整个任务，应该优先尝试一次性执行完这些所有的步骤。

## 步骤 1: 理解代码

充分理解用户指定的代码及其所有相关依赖，输出一份**代码理解报告**。

### 阅读范围

- 目标模块的 `.h` 头文件：理解每个方法的签名、参数含义、返回值
- 目标模块的 `.cpp` 源文件：了解当前是空壳还是部分实现
- 目标模块依赖的下游模块（被调用的类/函数）
- 目标模块的上游调用者（谁在使用这些接口）

### 输出：代码理解报告

阅读完成后输出一份简短报告，包含以下内容：

1. **接口列表** — 所有 public 方法的签名、功能简述、返回值含义
2. **依赖关系** — 调用了哪些外部类/方法，调用链是什么
3. **关键数据结构** — 涉及的核心数据结构（页面、记录、索引节点等）及其不变式
4. **注意事项** — 哪些方法有副作用（写磁盘、修改状态）、哪些依赖外部状态、哪些操作不线程安全、容易出错的地方

## 步骤 2: 记录待测接口清单

从步骤 1 的代码理解报告中提取需要测试的单元清单，作为后续设计用例的检查列表。

每个待测单元需标明：

| 字段 | 说明 |
|------|------|
| **单元** | 类名、方法名或数据结构名 |
| **类型** | 单方法 / 方法组合 / 数据结构 / 跨模块协作 |
| **优先级** | 高（核心路径）/ 中（辅助功能）/ 低（边界场景） |
| **依赖** | 该单元依赖哪些其他模块或方法 |

示例格式：

```
待测单元: DiskManager::create_file
  类型: 单方法
  优先级: 高
  依赖: 文件系统

待测单元: DiskManager::write_page + read_page 协作
  类型: 方法组合
  优先级: 高
  依赖: create_file
```

清单完成后与用户确认，确保没有遗漏关键接口。

## 步骤 3: 设计用例

对清单中每个待测单元设计三类测试：

| 类型 | 说明 |
|------|------|
| 正常路径 | 基本功能是否正常工作 |
| 异常路径 | 错误输入时是否抛出正确的异常 |
| 边界条件 | 极限值（第 0 页、空文件、多文件等） |

## 步骤 4: 编写测试文件（分层）

测试按颗粒度从细到粗分三层编写，确保每个最小颗粒度正确后再往上构建。

### L1: 单方法基本行为

测试每个方法的**最小颗粒度正确性**——一个 TEST_F 只验证一个方法的一个行为：

- 方法是否能成功调用
- 返回值是否符合预期
- 内部状态是否正确更新（通过 `#define private public` 验证）
- 错误参数是否抛出预期异常

目标：**每个方法独立正确**。

### L2: 方法协作 / 功能级别

测试多个方法组合完成一个功能：

- `create_file` → `write_page` → `read_page` 验证读写一致性
- `open_file` → `list_files` 验证文件列表正确
- 多次写入后的状态累积是否正确

目标：**方法之间协作正确**。

### L3: 跨模块联调

测试多个模块的交互：

- DiskManager + BufferPoolManager 的页面流转
- Record + Index 的插入查找链路

目标：**模块边界正确**。L3 测试的依赖模块可能尚未实现，初始运行预期 **FAIL**，随实现逐步变绿。

### 文件组织

```
our-test/<模块名>/
├── 00-all_test.cpp          # C++ 一键运行入口，自带 main() + 横幅 + RUN_ALL_TESTS()
├── 01-<接口1>_test.cpp      # 一个测试文件只测一个接口
├── 02-<接口2>_test.cpp
├── ...
└── CMakeLists.txt
```

### 文件顶部必须写清运行命令

```cpp
/**
 * @file 01-create_file_test.cpp
 * @brief 测试 DiskManager::create_file
 *
 * 运行方式（单独运行）:
 *   cd build && make 01-create_file_test && ./bin/01-create_file_test
 *
 * 运行方式（一键全部）:
 *   cd build && make run_all_disk_tests
 */
```

### 单个测试文件规范

- 文件头用 `@file` + `@brief` 注释说明测试对象，附运行命令
- 每个 `TEST_F` 上方有注释块：**测试目的**、**过程**、**预期**
- 独立的 Fixture 类，SetUp 创建测试目录并 chdir 进入，TearDown 返回并清理
- 用 `#define private public` / `#undef private` 访问私有成员验证内部状态
- 文件内测试按 L1 → L2 → L3 顺序排列，用注释分隔层次

### 测试输出用中文打印

测试输出要像一份中文测试报告，每条打印包含：目的、过程、输入、输出。

规则：
1. 所有 `std::cout` 用中文描述
2. 开头说明这个用例要验证什么
3. 打印关键输入值
4. 打印关键步骤说明
5. 断言前打印返回值、状态
6. 每行控制在一句话内，避免信息爆炸

```cpp
TEST_F(FooTest, Basic) {
    std::cout << "--- 基本创建 ---" << std::endl;
    std::cout << "目的: 创建文件后通过 is_file 确认其存在" << std::endl;
    std::cout << "输入: path=" << PATH << std::endl;
    dm_->create_file(PATH);
    std::cout << "输出: is_file=" << dm_->is_file(PATH) << std::endl;
    EXPECT_TRUE(dm_->is_file(PATH));
}
```

### 00-all_test.cpp 规范

- 真正的 C++ 程序（不是 shell 脚本）
- 文件顶部写清一键运行命令
- 提供自己的 `main()`，链接 `gtest`（非 `gtest_main`）
- 启动时打印横幅，列出所有测试文件和用例总数
- 每个测试文件之间用 `┌─...─┐` 框分隔
- 最后输出汇总表 + ALL PASSED / 部分 FAILED（L3 预期 FAIL 标为已知）
- 注册自定义 Listener 接管输出格式，关闭默认 printer
- 调用 `RUN_ALL_TESTS()` 并返回结果

## 步骤 5: 编写 CMakeLists.txt

- 每个测试文件一个独立的 `add_executable`，链接 `gtest_main`
- `00-all_test` 编译所有 .cpp 文件，链接 `gtest`（不用 gtest_main，因为自带 main）
- 添加 `add_custom_target(run_all_xxx)` 方便 `make run_all_xxx` 一键编译运行

## 步骤 6: 集成到构建系统

在 `src/CMakeLists.txt` 末尾添加：
```cmake
add_subdirectory(../our-test/<模块名> ${CMAKE_BINARY_DIR}/our-test/<模块名>)
```

## 步骤 7: 验证

```bash
cd build && cmake .. && make 00-all_test && ./bin/00-all_test   # 一键
cd build && make 01-xxx_test && ./bin/01-xxx_test                # 单独
```

L1 测试应全部 PASS（基本行为正确），L2 测试逐步变绿（功能协作正确），L3 联调测试预期 FAIL 直到依赖模块实现完成。
