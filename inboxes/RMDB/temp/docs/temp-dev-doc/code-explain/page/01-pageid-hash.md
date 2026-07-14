# 01-PageId 的 Get()、PageIdHash、std::hash 三者的区别

## 问题

`page.h` 中 `PageId` 有三个相关函数：`Get()`、`PageIdHash`、`std::hash<PageId>`。各自在什么场景下使用？为什么需要三个？

## 通俗理解

把 `PageId` 想象成一张门禁卡，卡上印着**楼号 fd** 和**房间号 page_no**。要把这些卡存进一个有几万格抽屉的大卡柜（`unordered_map`），需要决定每张卡放哪个抽屉。

## Get()：把卡面信息念成一串数字

```cpp
int64_t Get() const { return (static_cast<int64_t>(fd) << 16) | page_no; }
```

就是个打包工具。`fd=3, page_no=5` → `196613`。你想知道"这张卡的唯一数字编号是多少"，用它。**它不负责分抽屉。**

## PageIdHash：手动告诉卡柜用哪个抽屉

```cpp
struct PageIdHash {
    size_t operator()(const PageId &x) const { return (x.fd << 16) | x.page_no; }
};
```

`unordered_map` 不认识你自定义的 `PageId`，不知道按什么规则分抽屉，所以你必须**显式**告诉它。项目中就这样用：

```cpp
// BufferPoolManager 的私有成员
std::unordered_map<PageId, frame_id_t, PageIdHash> page_table_;
//                  ^key    ^value      ^"用这个规则分抽屉"
```

每次声明 map 都要把 `PageIdHash` 写在尖括号里。

## std::hash\<PageId\>：一次性教会卡柜自动识别

```cpp
template <>
struct std::hash<PageId> {
    size_t operator()(const PageId &obj) const { return std::hash<int64_t>()(obj.Get()); }
};
```

这是教给 C++ 标准库："以后碰到 `PageId`，一律用这个规则分抽屉"。教完之后就省事了：

```cpp
// 不写 hash 了，编译器自动找到 std::hash<PageId>
std::unordered_map<PageId, frame_id_t> map;
```

## 为什么 PageIdHash 是冗余的

两个哈希做的是同一件事（`fd << 16 | page_no`），只是用法不同：

| | 怎么用 |
|---|---|
| `PageIdHash` | 每次声明 map 都要手写 `unordered_map<PageId, V, PageIdHash>` |
| `std::hash<PageId>` | 教一次，之后直接 `unordered_map<PageId, V>` 就行 |

有了 `std::hash<PageId>` 特化之后，`PageIdHash` 就不需要了。项目中两个都留着只是还没清理。

## 一个真实隐患

`(fd << 16) | page_no` 给 `fd` 只留了 16 位。如果 `page_no > 65535`，它的高 16 位会和 `fd` 重叠：

```
PageId{fd: 5, page_no: 0}      → (5 << 16) | 0       = 桶 327680
PageId{fd: 0, page_no: 327680} → (0 << 16) | 327680   = 桶 327680  ← 撞桶
```

两张不同的卡进了同一个抽屉。虽然 `operator==` 能正确区分它们（在抽屉里逐一对比），但撞桶多了抽屉变链表，查找就慢了。实际上 4KB 页 × 65535 ≈ 256MB 的表才会触发，教学中不大可能出现。更稳的写法是给 `fd` 留 32 位：

```cpp
return (static_cast<int64_t>(fd) << 32) | static_cast<uint32_t>(page_no);
```
