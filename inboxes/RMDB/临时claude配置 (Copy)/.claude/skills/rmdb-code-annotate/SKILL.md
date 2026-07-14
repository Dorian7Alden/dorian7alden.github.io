---
name: rmdb-code-annotate
description: RMDB 项目源码注释专用技能。当用户要求给指定的函数/代码块"加注释"、"补充注释"、"写注释"、"标注操作"、"标注代码块"时触发。只对 src/ 下的 C++ 代码生效。
---

# RMDB 代码注释

给指定函数的代码块补充内联注释：将函数体内的操作按逻辑分组，一组一行注释。

## 核心原则

- **只描述动作，不解释原因**。注释说"做了什么"，不说"为什么这么做"。
- **中文，一行内，控制在 20 字以内**。
- **按逻辑块分组**——几行代码完成同一个语义动作的，归为一组，前面加一行注释。
- **不逐行注释**。如果连续多行都在做同一件事（如读取字段、赋值），合并为一组。
- **不注释显而易见的操作**。`return true`、`if (xxx)` 不加注释。

## 什么是逻辑块

逻辑块是函数体内若干行代码，它们共同完成一个可命名的动作。例子：

| 代码 | 逻辑块注释 |
|------|-----------|
| `page_table_.erase(id); page->reset_memory(); page->id_.page_no = INVALID; free_list_.push(frame);` | `// 注销旧页，归还帧到 free_list_` |
| `replacer_->pin(frame_id); page->pin_count_ = 1;` | `// 固定帧，pin_count 置 1` |
| `flush_log_before_page_write(page); disk_manager_->write_page(...); page->is_dirty_ = false;` | `// 先刷 WAL 再落盘，清除脏标记` |

## 工作流程

1. 用户指定目标函数名（如 `fetch_page`、`update_page`）
2. 读取该函数所在文件，定位函数体
3. 识别函数体内的逻辑分组
4. 为每组添加一行中文注释（不改动代码逻辑）
5. 编译验证
