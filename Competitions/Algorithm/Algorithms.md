## 算法分类



---



### 二分法查找

- 查找区间特点 [l, r] ? [l, r) ? (l, r]

```c++
int findByTo(int* arr, int size, int target)  // 前提：数组有序排列 sort
{  // 左闭右闭区间[]内找数
    int l = 0, r = size - 1, mid;
    while (l <= r)  
    {  // 当边界相等时，表达式也要成立 l=2, r=2, 2<=2 成立
        mid = l + (r - l) / 2;  // 不要用(l+r)/2，可能导致超过int类型最大值溢出
        if (arr[mid] > target) r = mid - 1;  // 排除mid之后的下一个数当作新边界
        else if (arr[mid] < target) l = mid + 1;  // 排除mid之后的下一个数当作新边界
        else return mid;
    }
    return -1;
}
```



---



### 前缀和与差分

二维的前缀和



---



### 双指针

1. 数组两个指针 slow, fast，一次循环
2. 分析数据特征，确定指针方向，从左到右？从右到左？两边向中间收敛？
3. 哪个指针先动？哪个后动？运动条件判断



---



### 滑动窗口







---



### 哈希表

> 反应元素在集合中的情况 （是否出现）（重复）
>
> 元素很大|元素很分散 时不适合用数组当hash表

1. 一个数在集合里面是否出现
2. 两个数的和在集合里面是否出现
3. 遍历一个数，加双指针，操作三个数
4. 四个数变两个两数和，操作四个数
5. 两数相等 == a在b的集合中
6. 查表找值，用unorderd_set | unordered_map，哈希法实现，速度更快，消耗空间



---



### 栈与队列

栈实现队列：入栈 --> 出栈，两个栈，方向不同

队列实现栈：弹出元素再添加元素，直到最后一个元素，一个队列实现栈





---



### 贪心

> 局部最优解推全局最优解

1. 将问题分解为若干个子问题
2. 找出适合的贪心策略
3. 求解每⼀个子问题的最优解
4. 将局部最优解堆叠成全局最优解



---



### 回溯

> backtracking 递归函数
>
> 模板
>
> ```c++
> void backTracking(vars) {
> 	if (end?) {
> 		收集结果;
> 		return;
> 	}
> 	for (集合元素) {
> 		处理子节点；
> 		递归函数；
> 		回溯操作；
> 	}
> 	return;
> }
> 
> ```
>
> 

排列组合的区别，能否重复

三部曲

- 递归函数的参数与返回值

- 确定终止条件

- 单层递归逻辑

步骤点：

- 确定状态
- 非法状态（return）
- 更新状态
- 结束状态
- 状态转移（搜索下一个状态）
- 还原状态



---



### DFS

Leetcode 98 [验证二叉搜索树](https://leetcode.cn/problems/validate-binary-search-tree/)

~~~c++
class Solution {
public:
    bool isValidBST(TreeNode* root) {
		return dfs(root, LONG_MIN, LONG_MAX);
    }
    
    bool dfs(TreeNode* node, long l, long r) {
    	if (node == nullptr) return true;
    	if (node->val <= l || node->val >= r) return false;
    	
    	return dfs(node->left, l, node->val) && dfs(node->right, node->val, r);
	}
};

~~~











---



### 动态规划

> 涉及很多重叠的子问题。每个状态由上一个状态推出来。

1. 确定dp数组以及下标的含义
2. 确定递推公式
3. dp数组如何初始化
4. 确定遍历顺序
5. 举例推导dp数组

细节经验：



dp背包问题：

1. 物品的重量
2. 物品的价值
3. 达到重量的组合数

CSP 37 2：[机器人饲养指南](https://sim.csp.thusaac.com/contest/37/problem/1)

- 每天投喂的苹果数量 --> 物品的重量
- 投喂苹果后获得的快乐值 --> 物品的价值
- 共有m中投喂方式 --> 组合数

```c++
#include<iostream>
#include<vector>
// #include<bits/stdc++.h>   // 引入所有标准库，一般不推荐使用，可能导致不必要的头文件引入
using namespace std;

int main(int argc, char const *argv[])
{
    int n, m;
    // 输入总苹果数（背包容量）n 和 投喂方式数量 m
    cin >> n >> m;
    
    vector<int> A(m);
    // 输入m个整数，代表每种投喂方式对应的收益(物品的重量为i+1,价值为A[i])
    for (int i = 0; i < m; i++){
        cin >> A[i];
    }
    
    // 创建 dp 数组，初始化为 0， dp[i] 代表容量为 i 时的最大价值
    vector<int> dp(n + 1, 0);

    // 遍历每个投喂方式(物品)
    for (int i = 0; i < m; i++){
        // 遍历容量，从当前投喂方式的数量开始，直到容量为 n
        // 这里 i+1 表示的是当前投喂方式对应的苹果数，因为 A[i] 代表每种方式的收益（苹果数）
        for (int j = i + 1; j <= n; j++){
            // 计算在当前容量下能获得的最大价值
            dp[j] = max(dp[j], dp[j - (i + 1)] + A[i]);
        }
    }
    
    // 输出最大值，即 dp[n]，代表容量为 n 时的最大快乐值
    cout << dp[n] << endl;
    

    return 0;
}

```



---

