# 蓝桥杯模拟题



---



## 蓝桥杯15界A组B题 : 五子棋对弈 : DFS经典



### 问题描述

"在五子棋的对弈中，友谊的小船说翻就翻？" 不！对小蓝和小桥来说，五子棋不仅是棋盘上的较量，更是心与心之间的沟通。这两位挚友秉承着"友谊第一，比赛第二"的宗旨，决定在一块 5×5 的棋盘上，用黑白两色的棋子来决出胜负。但他们又都不忍心让对方失落，于是决定用一场**和棋（平局）**作为彼此友谊的见证。

比赛遵循以下规则：

1. **棋盘规模**：比赛在一个 5×5 的方格棋盘上进行，共有 25 个格子供下棋使用。
2. **棋子类型**：两种棋子，黑棋与白棋，代表双方。小蓝持白棋，小桥持黑棋。
3. **先手规则**：白棋（小蓝）具有先手优势，即在棋盘空白时率先落子（下棋）。
4. **轮流落子**：玩家们交替在棋盘上放置各自的棋子，每次仅放置一枚。
5. **胜利条件**：率先在横线、竖线或斜线上形成连续的五个同色棋子的一方获胜。
6. **平局条件**：当所有 25 个棋盘格都被下满棋子，而未决出胜负时，游戏以平局告终。

在这一设定下，小蓝和小桥想知道，有多少种不同的棋局情况，既确保棋盘下满又保证比赛结果为平局。

### 答案提交

这是一道结果填空题，你只需要算出结果后提交即可。本题的结果为一个整数，在提交答案时只填写这个整数，填写多余的内容将无法得分。

### 答案

~~~c++
#include<bits/stdc++.h>
using namespace std;

int mp[10][10];	// map 为内置变量名
int ans=0;

void check() {
	
	int flag=0; // 检查棋子是否下满棋，白13，黑12
	for (int i=0; i<5; i++) {
		for (int j=0; j<5; j++) {
			if (mp[i][j]==1) flag++;
		}
	}5
	if (flag!=13) return;
	// 对角线 获胜
	if ((mp[0][0]+mp[1][1]+mp[2][2]+mp[3][3]+mp[4][4])%5==0) return;
	if ((mp[0][4]+mp[1][3]+mp[2][2]+mp[3][1]+mp[4][0])%5==0) return;
	// 横竖排 获胜
	for (int i=0; i<5; ++i) {
		if ((mp[i][0]+mp[i][1]+mp[i][2]+mp[i][3]+mp[i][4])%5==0) return;
		if ((mp[0][i]+mp[1][i]+mp[2][i]+mp[3][i]+mp[4][i])%5==0) return;
	}
	// 排除下满棋之后，没获胜即为和棋
	ans++;
}


void dfs(int cnt) {
	// 下棋 25 次
	if (cnt==25) {
		check();	
		return;
	}
	// 一个变量获取二维坐标
	int x = cnt/5;
	int y = cnt%5;
	// 该次下了白棋
	mp[x][y]=0;
	dfs(cnt+1);
	// 该次下了黑棋
	mp[x][y]=1;
	dfs(cnt+1);
}

signed main() {
	dfs(0);
	cout << ans << endl;
	return 0;
}

~~~



---



## 蓝桥杯15界A组C题 : 训练士兵 : 贪心困难



### **问题描述**

在蓝桥王国中，有 $n$ 名士兵，这些士兵需要接受一系列特殊的训练，以提升他们的战斗技能。对于第 $i$ 名士兵来说，进行一次训练所需的成本为 $p_i$ 枚金币，而要想成为顶尖战士，他至少需要进行 $c_i$ 次训练。

为了确保训练的高效性，王国推出了一种组团训练的方案。该方案包含每位士兵所需的一次训练，且总共只需支付 $S$ 枚金币（组团训练方案可以多次购买，即士兵可以进行多次组团训练）。

作为训练指挥官，请你计算出最少需要花费多少金币，才能使得所有的士兵都成为顶尖战士？

### **输入格式**

第一行包含两个整数 $n$ 和 $S$，表示士兵的数量和进行一次组团训练所需的金币数。

接下来的 $n$ 行，每行包含两个整数 $p_i$ 和 $c_i$，表示第 $i$ 名士兵进行一次训练的金币成本和要成为顶尖战士所需的训练次数。

### **输出格式**

输出一个整数，表示使所有士兵成为顶尖战士所需的最少金币数。

### 样例

#### 样例输入

```text
3 6
5 2
2 4
3 2
```

#### 样例输出

```text
16
```

#### 样例说明

花费金币最少的训练方式为：进行 2 次组团训练，花费 2×6=12 枚金币，此时士兵 1,3 已成为顶尖战士；再花费 4 枚金币，让士兵 2 进行两次训练，成为顶尖战士。总花费为 12+4=16。

### **评测用例规模与约定**

对于 40%40% 的评测用例，$1\leq n\leq10^3,1\leq p_i,c_i\leq10^5,1\leq S\leq10^7$。

对于所有评测用例，$1\leq n\leq10^{5},1\leq p_{i},c_{i}\leq10^{6},1\leq S\leq10^{10}$。

### 答案

~~~c++
#include<bits/stdc++.h>
using namespace std;
#define int long long

const int N = 1e5+100;
// 训练成本与训练次数绑定，可以尝试用pair
struct Node {
	int p;
	int c;
} mp[N];
int n, s, ans=0;

bool cmp(Node &n1, Node &n2) {
	return n1.c<n2.c;  // 多值变量需要自定义排序规则
}

signed main() {
	cin >> n >> s;
	
	for (int i=0; i<n; ++i) {
		cin >> mp[i].p >> mp[i].c;
	}
	// 涉及到贪心算法，条形图的线段，次数之类的题目，考虑先排序之后再思考。前提是没有顺序影响
	sort(mp, mp+n, cmp);
	// 一般来讲，组团训练成本低于单独训练
    // 排序之后，组团训练次数为一个节点，该节点前面的士兵已经全部训练完毕，后面的士兵需要再分析
    // 思考：如果这个节点后面的士兵的一次训练成本总和还大于组团训练的话，那么说明还能进行组团训练
    // 即，这个节点之后的士兵的一次训练成本总和一定要小于一次组团训练的成本
    // 因此，把训练过程划分为，节点之前全部组团训练，节点之后全部单独训练
	int sum=0;
	int pos;
	// 排序规则是训练次数从小到大，从后面开始遍历，累加一次的训练成本，如果大于等于一次组团训练成本
    // 那么该节点之后的所有士兵的单独的训练成本必然小于一次组团训练的成本
	for (int i=n-1; i>=1; --i) {
		sum+=mp[i].p;
		if (sum >= s) {
			pos = i;
			break;
		}
	}
	
	ans += s * mp[pos].c;
	for (int i=pos+1; i<n; ++i) {
		ans += (mp[i].c-mp[pos].c) * mp[i].p;
	}
	
	cout << ans << endl;
	
	return 0;
}
~~~



---



## 蓝桥杯15届A组D题 : 团建 : DFS树形结构



### 问题描述

小蓝正在和朋友们团建，有一个游戏项目需要两人合作，两个人分别拿到一棵大小为 $n$ 和 $m$ 的树，树上的每个结点上有一个正整数权值。

两个人需要从各自树的根结点 1 出发走向某个叶结点，从根到这个叶结点的路径上经过的所有结点上的权值构成了一个正整数序列，两人的序列的最长公共前缀即为他们的得分。给出两棵树，请计算两个人最多的得分是多少。

### 输入格式

输入的第一行包含两个正整数 $n, m$ 用一个空格分隔。

第二行包含 $n$ 个正整数 $c_1,c_2,\dots ,c_n$ 相邻整数之间使用一个空格分隔, 其中 $c_i$ 表示第一棵树结点 $i$ 上的权值。

第三行包含 $m$ 个正整数 $d_1,d_2,\dots,d_m$ 相邻整数之间使用一个空格分隔，其中 $d_i$ 表示第二棵树结点 $i$ 上的权值。

接下来 $n-1$ 行，每行包含两个正整数 $u_i,v_i$ 表示第一棵树中包含一条 $u_i$ 和 $v_i$ 之间的边。

接下来 $m-1$ 行，每行包含两个正整数 $p_i,q_i$ 表示第二棵树中包含一条 $p_i$ 和 $q_i$ 之间的边。

### 输出格式

输出一行包含一个整数表示答案。

### 样例

#### 样例输入1

```text
2 2
10 20
10 30
1 2
2 1
```

#### 样例输出1

```text
1
```

#### 样例输入2

```text
5 4
10 20 30 40 50
10 40 20 30
1 2
1 3
2 4
3 5
1 2
1 3
3 4
```

#### 样例输出2

```text
2
```

#### 样例说明

在第一个样例中，两个序列可以为 $[10,20],[10,30]$ ，最大前缀为 11;

在第二个样例中，两个序列可以为 $[10,20,40],[10,20,30]$ ，最大前缀为 22。

### 评测用例规模与约定

对于 20% 的评测用例， $1\leq n,m\leq500$ ;

对于所有评测用例，$1\leq n,m\leq2\times10^5,1\leq c_i,d_i\leq10^8,1\leq u_i,v_i\leq n\mathrm{,}1\leq p_i,q_i\leq m$ ，对于任意结点，其儿子结点的权重互不相同。

### 答案

~~~c++
#include <bits/stdc++.h>
using namespace std;
#define N 200005
// map建造树形结构
// 键为节点，值为子节点
// ！！！题目说了节点为唯一值！！！
unordered_map<int,vector<int>> m1,m2;//存储的是节点下标关系
int n,m,a1[N],a2[N],num_max;
void dfs(int n1,int n2,int count){
  if(a1[n1]!=a2[n2]) return;
  num_max=max(num_max,count+1);
  for(int i=0;i<m1[n1].size();i++){
    for(int j=0;j<m2[n2].size();j++){
      int x=m1[n1][i],y=m2[n2][j];
      dfs(x,y,count+1);
    }
  }
}
int main()
{
  cin>>n>>m;
  for(int i=1;i<=n;i++) cin>>a1[i];
  for(int i=1;i<=m;i++) cin>>a2[i];
  for(int i=1;i<=n+m-2;i++){
    int u,v; cin>>u>>v;
    if(u>v) swap(u,v);
    if(i<=n-1) m1[u].push_back(v);
    else m2[u].push_back(v);
  }
  dfs(1,1,0);//从第一层开始遍历
  cout<<num_max;
  return 0;
}
~~~



---





# Leetcode



## 热题100



### 矩阵



#### 48. 旋转图像

- 辅助数组
  - 观察旋转的数的变化规律。行跟列的变化公式
  - 用一个临时数组储存被占用的数的原数

```c++
class Solution {
public:
    void rotate(vector<vector<int>>& matrix) {
        int n = matrix.size();
        // C++ 这里的 = 拷贝是值拷贝，会得到一个新的数组
        auto matrix_new = matrix;
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                matrix_new[j][n - i - 1] = matrix[i][j];
            }
        }
        // 这里也是值拷贝
        matrix = matrix_new;
    }
};
```

- 原地旋转
  - 递推公式得规律式



- 用翻转代替旋转



### 二分查找



#### 74. 搜索二维矩阵

- 更新 left 跟 right 用 mid 的值，不再重新计算位置了。
- while 中的结束标志，[] ? [) ? (] ? () 
- 返回插入的下标为 left 
- 根据结束的取值边界调整边界
- 条件判断全用 else if 可以省略 continue 关键字

```c++
class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        int m=matrix.size(), n=matrix[0].size();
        int l=0, r=m*n-1, mid;
        while (l<=r) {
            mid = (r-l)/2 + l;
            int mid_num = matrix[mid/n][mid%n];
            if (mid_num > target) r = mid - 1;
            else if (mid_num < target) l = mid + 1;
            else return true;
        }
        return false;
    }
};
```



#### 34. 在排序数组中查找元素的第一个和最后一个位置

- 处理起始位置的方法最好也是二分，两个二分分别查找起止位置跟终止位置。O(2logn) 
- 我这里是一个二分查找到值再遍历边界，如果所有值都相等的话，那就是O(n)的时间复杂度，但是极端情况排序数组都不会这样1。

```c++
class Solution {
public:
    vector<int> searchRange(vector<int>& nums, int target) {
        int left=0, right=nums.size()-1,mid;

        while (left<=right) {
            mid=left + (right-left)/2;
            if (nums[mid]>target) right=mid-1;
            else if (nums[mid]<target) left=mid+1;
            else {
                int start=mid,end=mid;
                for (int i=start; i>=0; --i) {
                    if (nums[i]!=target) break;
                    start=i;
                }
                for (int i=end; i<nums.size(); ++i) {
                    if (nums[i]!=target) break;
                    end=i;
                }
                return vector<int>{start, end};
            }
        }
        return vector<int>{-1, -1};
    }
};
```



#### 33. 搜索旋转排序数组

- 二分法，另类的中点值判断

```c++
class Solution {
public:
    int search(vector<int>& nums, int target) {
        if (nums.size()==1) {
            if (target==nums[0]) return 0;
            else return -1; 
        } 
        int left=0;
        int right=nums.size()-1;
        int mid;

        while (left<=right) {
            mid=left+(right-left)/2;
            if (nums[mid]>nums[0]) left=mid+1;
            else if (nums[mid]<nums[0]) right=mid-1;
            else left=mid+1;
        }
        int s=left;        

        if (target>nums[0]) {
            left=0;
            right=s-1;
            while (left<=right) {
                mid=left+(right-left)/2;
                if (target>nums[mid]) left=mid+1;
                else if (target<nums[mid]) right=mid-1;
                else return mid;
            }
        } else if (target<nums[0]) {
            left=s;
            right=nums.size()-1;
            while (left<=right) {
                mid=left+(right-left)/2;
                if (target>nums[mid]) left=mid+1;
                else if (target<nums[mid]) right=mid-1;
                else return mid;
            }
        } else if (target==nums[0]) return 0;
        return -1;
    }
};
```





### 技巧



#### 136. 只出现一次的数字

```c++
class Solution { // 我的代码
public:
    int singleNumber(vector<int>& nums) {
        unordered_map<int, int>mp;
        int size = nums.size();

        for (int i=0; i<size; ++i) {
            int to = nums[i];
            if (mp.count(to)) mp[to]=2;
            else mp[to]=1;
        }
        for (int i=0; i<size; ++i) {
            if (mp[nums[i]]==1) return nums[i];
        }
        return 0;
    }
};
```

```c++
class Solution { // 最优解
public:
    int singleNumber(vector<int>& nums) {
        int ret = 0;
        for (auto e: nums) ret ^= e;
        return ret;
    }
};
```





#### 169.多数元素

我的代码

- 哈希表：统计每个数的和...sb做法。直接统计次数不好吗？多此一举而且还导致数值溢出了

```c++
class Solution {
public:
    int majorityElement(vector<int>& nums) {
        int size = nums.size();
        int cnt = size/2;
        unordered_map<long long,long long>mp;

        for (auto i: nums) {
            if (mp.count(i)==0) mp[i]=i;
            else mp[i]+=i;
        }

        for (unordered_map<long long,long long>::iterator it=mp.begin(); 
             it != mp.end(); 
             ++it) {
                if (abs(it->second) > abs(it->first*cnt)) return it->first;
            }

        return 0;
    }
};
```

技巧解

- 排序：多数可以理解为众数。直接排序+返回中值即可

- Boyer-Moore 投票算法：维护一个预定值，一个预定值的次数统计。如果是预定值次数+1，如果不是则-1，次数为0时更新预定值。

```c++
class Solution {
public:
    int majorityElement(vector<int>& nums) {
        int candidate = -1;
        int count = 0;
        for (int num : nums) {
            if (num == candidate) ++count;
            else if (--count < 0) {
                candidate = num;
                count = 1;
            }
        }
        return candidate;
    }
};
```







































## 每日一题



### 2106. 摘水果



#### 我的代码

- 越界。没有判断遍历的水果个数，可能每个水果都在移动的范围内，没有限制个数。
- 超时。时间复杂度为：O(k*n) k = 2e5, n = 1e5 最大为1e10

```c++
class Solution {
public:
    int maxTotalFruits(vector<vector<int>>& fruits, int startPos, int k) {
        int ans = 0;
        int n = fruits.size();
        const int MAX_POS = 2e5;
        int l, r, s;
        int right_bound, left_bound;
        for (l=0; l<=k; ++l) {
            r = k - l;
            if (l >= r) { // right first
                right_bound = startPos + r;
                left_bound = right_bound - l;
                if (right_bound > MAX_POS) continue;
                s = 0;
                for (int i=0; i < n && fruits[i][0] <= right_bound; ++i) {
                    if (fruits[i][0] < left_bound) continue;
                    s += fruits[i][1];
                }
                ans = max(ans, s);
            }
            if (r >= l) { // left first
                left_bound = startPos - l;
                right_bound = left_bound + r;
                if (left_bound < 0) continue;
                s = 0;
                for (int i=0; i < n && fruits[i][0] <= right_bound; ++i) {
                    if (fruits[i][0] < left_bound) continue;
                    s += fruits[i][1];
                }
                ans = max(ans, s);
            }
        }
        return ans;
    }
};
```



#### 答案

- 算法：前缀和+二分查找
- 



#### 经验

- 遍历的时候，使用前缀和时，使用 `sum[i+1] = sum[i] + value[i+1]` ，而不用 `sum[i] = sum[i-1] + value[i]` 效果更好。避免越界0，只需创建数组的时候空间大1。 初始化比较麻烦。



#### 题解

##### 前缀和+二分查找

- 前缀和计算每个有水果的位置的水果总数
- 二分查找在移动范围内的水果的下标边界

```c++
class Solution {
public:
    int maxTotalFruits(vector<vector<int>>& fruits, int startPos, int k) {
        int n = fruits.size();
        vector<int> sum(n + 1);
        vector<int> indices(n);
        for (int i = 0; i < n; i++) {
            sum[i + 1] = sum[i] + fruits[i][1];
            indices[i] = fruits[i][0];
        }
        int ans = 0;
        for (int x = 0; x <= k / 2; x++) {
            /* 向左走 x 步，再向右走 k - x 步 */
            int y = k - 2 * x;
            int left = startPos - x;
            int right = startPos + y;
            int start = lower_bound(indices.begin(), indices.end(), left) - indices.begin();
            int end = upper_bound(indices.begin(), indices.end(), right) - indices.begin();
            ans = max(ans, sum[end] - sum[start]);
            /* 向右走 x 步，再向左走 k - x 步 */
            y = k - 2 * x;
            left = startPos - y;
            right = startPos + x;
            start = lower_bound(indices.begin(), indices.end(), left) - indices.begin();
            end = upper_bound(indices.begin(), indices.end(), right) - indices.begin();
            ans = max(ans, sum[end] - sum[start]);
        }
        return ans;
    }
};
```



#### 滑动窗口



#### 总结

- 分析移动位置的策略（贪心尽可能最多水果）:

  - 只往一个方向走
  - 先去一个方向再去反方向
  - 在边界往另一个方向走

  - 总结：先去一个方向再去反方向可以包含另外两种情况

- 可以使用前缀和在 O(1) 的时间内计算出范围内的水果数，减少遍历的次数。（我只需要使用前缀和即可AC这道题）

- 如果知道了有一般的遍历无意义，可以通过限定临界点减少遍历次数。最多往一个方向走k/2步（贪心）。

- 只有两个方向，选择数少，就不用再判单是往哪个方向了，直接遍历向左走，再尝试向右走。

- 尽量减少变量的使用，有了l，r = k-l，不要再增加 r 变量了，直接用公式计算。

- 前缀和：每个位置的最大水果数量 ? 每个有水果位置的最大水果数量





### 904. 水果成篮

- 滑动窗口 + 哈希表

```c++
class Solution {
public:
    int totalFruit(vector<int>& fruits) {
        int n = fruits.size();
        unordered_map<int, int> cnt;

        int left = 0, ans = 0;
        for (int right = 0; right < n; ++right) {
            ++cnt[fruits[right]];
            while (cnt.size() > 2) {
                auto it = cnt.find(fruits[left]);
                --it->second;
                if (it->second == 0) {
                    cnt.erase(it);
                }
                ++left;
            }
            ans = max(ans, right - left + 1);
        }
        return ans;
    }
};
```

- 总结
  - 哈希表：数组存次数，而不是存位置
  - 维护次数比维护位置简便些
  - 只要保证是两种水果就行了。没说必须将一种水果从头取到尾，可以从中间截断
  - map操作，auto it = map.find(); --it->second; cnt.erase(it); find返回的是指针
  - n = vector.size()





### end



