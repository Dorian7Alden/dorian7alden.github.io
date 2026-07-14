# 02-PageId 哈希算法优化（未实施，待改进）

## 当前状态

`src/storage/page.h` 中的 PageId 哈希：

```cpp
// PageId::Get()
inline int64_t Get() const { return (static_cast<int64_t>(fd) << 16) | page_no; }

// PageIdHash — 显式指定
struct PageIdHash {
    size_t operator()(const PageId &x) const { return (x.fd << 16) | x.page_no; }
};

// std::hash<PageId> — 标准库特化
template <>
struct std::hash<PageId> {
    size_t operator()(const PageId &obj) const { return std::hash<int64_t>()(obj.Get()); }
};
```

三个哈希器实际上用的都是同一个 `(fd << 16) | page_no`。

## 存在的问题

1. **PageIdHash 冗余**：有了 `std::hash<PageId>` 特化后，`PageIdHash` 不再需要。两个 `unordered_map` 显式指定 `PageIdHash` 也是多余的
2. **分布不均匀**：`(fd << 16) | page_no` 是简单的位拼接，fd 通常是 3~7 的小整数，page_no 在 0~几万。哈希值低位完全由 page_no 决定，高位变化极少，桶分布不均匀
3. **page_no 高位碰撞**：page_no ≥ 65536 时高位覆盖 fd 区域，不同 PageId 落入同一桶

## 参考方案

来自 `src/` 参考实现的思路（`/home/dorian/Desktop/PageId哈希处理详解.md`）：

### 哈希算法改用 std::hash 组合

```cpp
// 替代 (fd << 16) | page_no
namespace std {
template <>
struct hash<PageId> {
    size_t operator()(const PageId &obj) const {
        std::size_t h1 = std::hash<int>{}(obj.fd);
        std::size_t h2 = std::hash<page_id_t>{}(obj.page_no);
        return (h1 << 1) ^ (h2 << 1 >> 1);  // h1 左移扩散，异或混合 h2
    }
};
}
```

优势：`std::hash` 内置雪崩效应，把连续的小整数打散成均匀分布的哈希值，再通过移位+异或组合，两个字段的影响充分混入最终结果。

### 去掉冗余哈希器

- 删除 `PageIdHash` 结构体
- 删除 `PageId::Get()`（或保留但不用于哈希）
- `std::hash<PageId>` 作为唯一哈希入口

### 可选：缓冲池多实例分片

参考实现将 BufferPoolManager 拆成 1 个 Manager + 16 个 Instance，通过 `hasher_(page_id) % 16` 把页面请求均匀分散到不同实例，每个实例有独立的 `latch_`。多线程并发时锁争用降低约 16 倍。

```cpp
// 在 BufferPoolManager 中加入路由
inline std::size_t get_instance_no(const PageId &page_id) {
    return std::hash<PageId>{}(page_id) % BUFFER_POOL_INSTANCES;
}

Page *fetch_page(PageId page_id) {
    return instances_[get_instance_no(page_id)]->fetch_page(page_id);
}
```

这是架构级改动，成本高但收益大。

## 实施优先级建议

| 优先级 | 改动 | 成本 | 收益 |
|--------|------|------|------|
| 高 | 删掉 PageIdHash，统一用 std::hash<PageId> | 极小 | 去冗余，代码更干净 |
| 中 | 哈希算法改为 std::hash 组合 | 小 | 改善分布，减少碰撞 |
| 低 | 缓冲池 16 实例分片 | 大 | 降低锁争用，提升并发 |

### 待研究：一个哈希函数够用吗

统一用 `std::hash<PageId>` 意味着所有场景共享同一个哈希函数。但不同场景对哈希的侧重点不同：

| 场景 | 容器 | 条目数 | 核心诉求 |
|------|------|--------|----------|
| `page_table_` 帧查找 | `unordered_map` | 最多 65536 | 桶内均匀，减少碰撞退化 |
| `version_info_` 版本查找 | `unordered_map` | 几十 ~ 数十万 | 同上 |
| 多实例路由 | `% BUFFER_POOL_INSTANCES` | — | 页面均匀分散到各实例，**负载均衡**优先 |

前两个场景关心的是"同一桶内打架少"，第三个关心的是"不同实例间任务均匀"。同一个哈希函数可能无法同时最优：

- 哈希值的**高位**决定路由（`% 16` 只看低 4 位），如果哈希值的低位分布不均匀，某些实例会负载偏高
- 哈希值的**全位**决定桶定位，碰撞率受整体分布影响

一个更精细的方案可能是**分离路由哈希和查找哈希**：

```cpp
// 路由哈希：专门负责 %INSTANCES，关注低位的均匀性
size_t routing = hash_routing(page_id) % BUFFER_POOL_INSTANCES;

// 实例内查找：instance[].page_table_ 用另一个哈希，关注全位碰撞率
instance[routing]->fetch_page(page_id);  // 内部用 hash_lookup(page_id)
```

但这增加了复杂度——两个哈希函数要各自维护，且保证一致性。是否值得，取决于实测中路由不均或碰撞退化的严重程度。

> **待验证**：在多实例分片 + 大数据集下，测量各实例的页面分布方差和 page_table_ 的平均链长。如果单哈希已经足够均匀，就不需要分离。

## 不现在做的原因

- 当前单实例 BufferPoolManager 的 `latch_` 已串行化所有操作，哈希分布质量对单实例的影响有限
- 如果后续引入多实例分片，哈希改法和分片可以一起做，一次性到位
