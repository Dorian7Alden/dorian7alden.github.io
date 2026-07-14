# 05-空函数体、__attribute__ 与 unused 的含义

## 问题

`disk_manager.cpp:74`：

```cpp
void DiskManager::deallocate_page(__attribute__((unused)) page_id_t page_id) {}
```

函数体是空的 `{}`、`__attribute__` 是什么、`unused` 有什么用？

## 空函数体：桩函数

`deallocate_page` 是"回收页面"的接口，功能尚未实现。头文件已经声明了它，必须提供定义，所以放一个空壳占位：

```cpp
void DiskManager::deallocate_page(page_id_t page_id) {}
```

## __attribute__((unused))：抑制编译警告

`__attribute__` 是 GCC/Clang 的编译器扩展语法（非 C++ 标准），用来给编译器传递额外指令。`unused` 属性告诉编译器"这个参数我知道没用到，不要报警告"。

不加 `unused` 的话，用 `-Wall` 编译会报：
```
warning: unused parameter 'page_id' [-Wunused-parameter]
```

加了就安静通过。这个警告本身是合理的——声明了参数但不用通常意味着有遗漏——但桩函数是有意不用的，所以显式标注压制。

## 另一种标准写法

C++17 提供了标准替代方案：`[[maybe_unused]]`，效果相同且跨平台：

```cpp
void DiskManager::deallocate_page([[maybe_unused]] page_id_t page_id) {}
```
