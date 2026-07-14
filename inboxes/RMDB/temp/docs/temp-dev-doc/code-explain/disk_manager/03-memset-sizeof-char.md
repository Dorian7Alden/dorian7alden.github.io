# 03-memset 中除以 sizeof(char) 的原因

## 问题

`disk_manager.cpp:20` 的构造函数：

```cpp
DiskManager::DiskManager() {
    memset(fd2pageno_, 0, MAX_FD * (sizeof(std::atomic<page_id_t>) / sizeof(char)));
}
```

数组元素类型是 `std::atomic<page_id_t>`，为什么 memset 的第三个参数要除以 `sizeof(char)`？

## 结论：完全多余

C++ 标准保证 `sizeof(char) == 1`，永远成立。所以：

```
sizeof(std::atomic<page_id_t>) / sizeof(char)
= sizeof(std::atomic<page_id_t>) / 1
= sizeof(std::atomic<page_id_t>)
```

以下两种写法完全等价：

```cpp
memset(fd2pageno_, 0, MAX_FD * sizeof(std::atomic<page_id_t>));
memset(fd2pageno_, 0, MAX_FD * (sizeof(std::atomic<page_id_t>) / sizeof(char)));
```

## memset 只认字节

`memset` 的签名是 `void *memset(void *s, int c, size_t n)`，第三个参数只关心**字节数**，与元素类型无关。它按字节逐个填入 `c` 的值，不关心你原本是什么类型。

除以 `sizeof(char)` 可能是作者的编码习惯，显式标注"以 char 为单位"的计算过程，但语义上没有任何作用。

## 是否影响性能

不影响。`sizeof` 是编译期运算符，整个表达式在编译时就被计算为常量 `32768`（`8192 × 4`），直接嵌入机器码。运行时既没有除法指令，也没有额外的加法——源码中的除号只存在于文本层面，二进制里就是一个立即数。
