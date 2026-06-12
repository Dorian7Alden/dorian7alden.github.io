## 2026-04-01 星期三



---

算法：

- 遍历 map 

    ```C++
    for (auto& [num, freq] : count) {
        bucket[freq].push_back(num);
    }
    ```

- multiset 数据结构，使用 next(addr, offset), prev() 进行寻址操作。
- TODO: 手写快排
- [数组中的第K个最大元素](https://leetcode.cn/problems/kth-largest-element-in-an-array/)、[前 K 个高频元素](https://leetcode.cn/problems/top-k-frequent-elements/)、[数据流的中位数](https://leetcode.cn/problems/find-median-from-data-stream/) 















