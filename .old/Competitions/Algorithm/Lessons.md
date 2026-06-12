# 位运算

- 与 &

- - 只有同时为1才输出1，其余输出0。（0为False，1为True，&&）
  - 判断是否被2整除：(n%2==0) --> (n&1\==0)
  - 判断是否为2的次幂：if (n&(n-1)) not else yes
  - 

- 或 |

  - 顾名思义
  - 

- 异或 ^ （做减法）

  - 任何数与0做异或运算，结果仍然是原来的数

  - 任何数和其自身做异或运算，结果是0

  - 异或运算满足交换律和结合律

  - 案例：

    - 使特定位翻转:  例：X=10101110，使X低4位翻转，用X ^ 0000 1111 = 1010 0001即可得到。
    - A^B^B = A
    - 交换二个数：a  =a ^ b;  b = b ^ a;  a = a ^ b;

  - ```c++
    x ^ 0 = x
    x ^ x = 0
    x ^ y ^ z = y ^ x ^ z = x ^ (y ^ z)
    ```

- 取反 ~

  - 补码，0 -> 1，1 -> 0

- 左移 <<

  - 当高位溢出时不是1，那么向左移一位就等于乘2

- 右移 >>

  - 根据有无符号，有符号是算术移位，无符号是逻辑移位
  - 移入0的称为“逻辑移位”,即简单移位；移入1的称为“算术移位”。



# vector初始化



## 初始化不同的值用 {v1, v2, v3, ...}

```c++
#include<bits/stdc++.h>
using namespace std;

signed main() {
	
	vector<int>a{1,2,3};
	for (int i=0; i<a.size(); i++) {
		cout << a[i] << " ";
	}
	
	return 0;
}
```



## 初始化相同的连续值用 (cnt， v)

```c++
#include<bits/stdc++.h>
using namespace std;

signed main() {
	
	vector<int>a(5, 1);
	for (int i=0; i<a.size(); i++) {
		cout << a[i] << " ";
	}
	
	return 0;
}
```



## 初始化二维不同

```c++
#include<bits/stdc++.h>
using namespace std;

signed main() {
	
	vector<vector<int>>a{vector<int>(5, 1), vector<int>(5, 2), vector<int>(5, 3)};
	for (int i=0; i<a.size(); i++) {
		for (int j=0; j<a[0].size(); j++) {
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
	
	return 0;
}
```



## 初始化二维相同

```c++
#include<bits/stdc++.h>
using namespace std;

signed main() {
	
	vector<vector<int>>a(5, vector<int>(5, 1));
	for (int i=0; i<a.size(); i++) {
		for (int j=0; j<a[0].size(); j++)
			cout << a[i][j] << " ";
		cout << endl;
	}
	
	return 0;
}
```





##  Tips



---



### 读取每行

```c++
#include <bits/stdc++.h>
using namespace std;

vector<vector<string> > read_line(vector<vector<string> > lines, int line_max=10) {
	string s;
	int line_index=0;
	while (cin >> s) {
        // 确保行存在（至少为cnt+1）（第一行 -> cnt=0）
        if (lines.size() <= line_index) {
            lines.push_back({}); // ÐÂÔöÒ»ÐÐ
        }
        // 上一个字符不是换行符
        lines[line_index].push_back(s);
        // 检查下一个字符是否为换行符
        if (cin.get() == '\n') {
            line_index++; // 切换下一行
        }
        // 读取达到最大行数结束
        if (line_index >= line_max) return lines;
    }
}

signed main() {
    int n;
	cin >> n;
    
    vector<vector<string> > li;
    li = read_line(li, n);

    // 打印结果
    for (int i = 0; i < li.size(); i++) {
        for (int j = 0; j < li[i].size(); j++) {
            cout << li[i][j] << " ";
        }
        cout << endl;
    }
	// 获取指令类型
	for (int i=0; i<n; i++) {
		int cmd = atoi(li[i][0].c_str());  // string to int
		cout << "cmd: " << cmd << endl;
	}
    
    return 0;
}
```



---



### 快速排序O(n)

~~~c++
#include<bits/stdc++.h>
using namespace std;

const int MAX = 1e4;//数太多了会爆内存，运行出错 

signed main() {
	int n=5;
	int nums[MAX+100], cnt[MAX]; 
	for (int i=0; i<n; ++i) { 
		cin>>nums[i];
		cnt[nums[i]]++;//储存这个数出现了多少次
	}
	for (int i=0, p=0; i<MAX; ++i) {
		while (cnt[i]-->0) {
			nums[p++]=i;
			cout << nums[p-1] << " ";
		}
	}
	return 0;
}
~~~



### 日期

获取日期的每位数字

公式：$n = date~~/~~10^{i-1}~~\%~~10~~(i：第~i~位数字)$

```c++
#include <bits/stdc++.h>
using namespace std;


signed main(){
	
	int date=20240413;
	
	for (int i=1; i<=8; i++) {
		cout << date / int(pow(10, i-1)) % 10 << endl;
	}
	
	return 0;
}
```

是否闰年

```c++
// 判断是否为闰年
bool isLeap(int year) {
    return ((year%4 == 0 && year % 100 != 0) || (year % 400 == 0));
}
```



---



### 质因数

~~~c++
#include<bits/stdc++.h>
using namespace std;

vector<int> divide(int x) {
	vector<int>a;
	for (int i=2; i<=x/i; ++i) {
		while (x%i==0) {
			x/=i;// 依次除以质因子
			a.push_back(i);
		}
	}
	if (x>1) a.push_back(x);
	return a;
} 

signed main() {
	vector<int>a = divide(18);
	for (int i=0; i<a.size(); i++) {
		cout << a[i] << endl;
	}
	return 0;
}
~~~



---



### 快速幂

> 快速求 $x^n$

~~~c++
#include<bits/stdc++.h>
using namespace std;

long long int quik_power(int base, int power) {
	long long int ret=1;
	while (power>0) {// 直到指数为1
		if (power % 2 == 1) {// 指数为奇数
			ret *= base;
			power--;
		}
        power/=2;
        base*=base;	
	}//底数与平方数的积
	return ret;
}

signed main() {
	cout << quik_power(2, 31) << endl;
	return 0;
}
~~~



### 排列组合数

> $C^m_{n+1} = C^{m}_{n} + C^{m-1}_n$        $C^m_n = C^{n-m}_n$        $C^m_n = \frac{A^m_n}{m!}$



---



### 素数

1. 所求范围很大时，不能直接判断一个数是否为质数，要遍历出非质数

2. 用两数相乘遍历出非质数

3. 两个循环，i，j，在l，r范围内循环，范围大小，r/i，i

```c++
#include<bits/stdc++.h>
using namespace std;

int p[100];
int l=101, r=150;
   
signed main() {
   	for (int i=2; i<=r/i; i++) {// i 遍历一个因子 
   		for (int j=r/i; j>=2; j--) {// j 遍历另一个因子 
   			if (i*j<l) break;
   			else p[i*j-l]=1;// 筛出含有因子的数为 1 (非质数) 
   		}
   	}
   	for (int i=l; i<=r; i++) {
   		cout << i; // 使用p[x-l]对应
   		p[i-l] ? cout<<" not prime":cout<<" yes prime";
   		cout << endl; 
   	}
   	return 0;
}
```

快速判断一个数是否为质数

~~~c++
bool isprime(int x) { // 判断一个数是否是素数
	if (x == 1) return false; // 注意这步特判是必需的
	for (int i = 2; i * i <= x; ++i)
		if (x % i == 0)
			return false;
	return true;
}
~~~

埃及法筛质数

~~~c++
#include<bits/stdc++.h>
using namespace std;

const int N = 1e6;
vector<bool>isPrime(N+100, true);
void sieve() {
    isPrime[0] = isPrime[1] = false;
	for (int i=2; i*i<=N; i++) {
		if (isPrime[i]) {
			for (int j=i*i; j<=N; j+=i) {
				isPrime[j]=false;
			}
		}
	}
}

signed main() {
	sieve();
	cout << isPrime[11111] << endl;
	return 0;
}
~~~



---



### 自定义排序 多个参数

sort排序的cmp，默认a<b从小到大为true，b>a从大到小为false

自定义一个cmp函数用来排序

~~~c++
#include<bits/stdc++.h>
using namespace std;

struct Node {
	int x, y;
} node[100];

bool cmp(Node &n1, Node &n2) {
	return n1.x > n2.x; // return 的是什么符号就是怎么排序，>: 从大到小（左大右小）
} 

signed main() {
	
	for (int i=0; i<5; ++i) {
		node[i].x = i;
		node[i].y = i+1;
		cout << "node[" << i << "]: " << node[i].x << ", " << node[i].y << endl;
	}
	
	cout << endl;
	
	sort(node, node+5, cmp);
	
	for (int i=0; i<5; ++i) {
		cout << "node[" << i << "]: " << node[i].x << ", " << node[i].y << endl;
	}
	
	return 0;
}
~~~



---



### 树形结构的另类构造

- 前提：当题目中明确表明节点的值为唯一值时，可以用 map 构造树形结构

  - key 表示唯一节点

  - value 用 vector\<int> 表示储存的子节点
  - 用一个数组接收每个节点的值



---



### 数组删除指定元素

- 双指针
- 时间复杂度：O(n)

```c++
int arr[] = { 2, 3, 2, 4, 54, 54, 354, 5, 23, 43 };
int slow = 0, fast, target = 2;
for (fast = 0; fast < sizeof(arr) / sizeof(arr[0]); fast++) {
    if (arr[fast] != target) {
        arr[slow++] = arr[fast];
    }
}
```



---



### GCD最简约分函数

```c++
int gcd(int a, int b)
{
	a = abs(a);
	b = abs(b);
	int temp;
    while (b != 0)
    {
        temp = b;
        b = a % b;
        a = temp;
    }
	return a;
}

int gcd(int a, int b) { return b ? gcd(b, a % b) : a;}
```

 ~~~c++
int gcd(int a, int b) {
    return b == 0 ? a : gcd(b, a % b);
}
 ~~~



### 最小公倍数

~~~c++
int lcm(int a, int b) {
    return a * b / gcd(a, b);
}
~~~





---



## 经验总结



---



### 合理运用位运算

```c++
int mid = (l + r) >> 1; // 除以2 可以为 >> 1
```



### 数组从1开始还是从0开始遍历？

- 当数组涉及到 i-1 时，要对前一个数组进行处理时，可以避免越界



### 查看数据类型范围

|          |          |
| -------: | :------- |
|  INT_MIN | INT_MAX  |
| LONG_MIN | LONG_MAX |
|          |          |



### 一个变量遍历二维

> 适用于 行列 数组

```c++
int x, y;
for (int i=0; i<25; ++i) {
	x = i/5;
    y = i%5;
}
```



### 优化速度

1. 赋值变量，防止重复计算

2. 判断奇偶数用位运算，a & 1 == 1为奇数，a & 1 == 0 为偶数

3. 迭代 > 递归

4. 用空间换时间

5. 算法不要超过$O(n^2)$

6. 1e5-1e6的输入输出用scanf，printf

7. ```c++
   ios::sync_with_stdio(false);
   cin.tie(0);
   cout.tie(0);
   // '\n'
   
   #define IOS ios::sync_with_stdio(false);cin.tie(0);cout.tie(0);
   ```

8. 万能头文件 <bits/stdc++.h>



### 循环

1. 固定循环边界，[x, y] ? [x, y) ? (x, y]



### 拆分思想

1. 四数之和 == 两对二数之和
2. 合二为一，整体思想





## string

| 函数                                       | 作用                                         |
| ------------------------------------------ | -------------------------------------------- |
| str.length(void)  \| str.size()            | 获取长度                                     |
| str.substr(int cnt)                        | 去掉cnt个字符前缀                            |
| for (int i=0; i<str.length(); i++)         | 下标操作字符                                 |
| str.insert(int index, string _str)         | 在下标index处插入 _str                       |
| str.append(string _str)                    | 末尾插入字符串                               |
| str + "string" \| "string" + str           | 快速拼接                                     |
| str.erase(int index, int cnt)              | 删除包括下标[index, index+cnt)的字符         |
| str.replace(int from, int to, string _str) | 将下标[from, to]的字符替换为字符串 _str      |
| str.find(string _str)                      | 查找子字符串，返回首字符的下标。没找到返回-1 |
| str.rfind(string _str)                     | 从后面开始找，首字符的下标                   |
| str.empty()                                | 是否为空字符串                               |
| str1 > \| < \| == str2                     | 字符串比较                                   |
| str.compare(str2)                          | 字符串比较(ASCII码值比较)                    |
| stoi(str) \| stof(str) \| stod(str)        | to int \| float \| double                    |
| getline(cin, string, ',')                  | 读取一行，结束符为‘,’                        |
| toupper(char) \| tolower(char)             | 大写字母 \| 小写字母                         |



## sstream库

> 对输入输出进行操作



### 构造函数的区别

~~~c++
#include<iostream>
#include<sstream>
using namespace std;

signed main() {
	stringstream ss1("hello world");
    stringstream ss2("hello");
    ss2 << "world";
    ss2 << "hi";
	// << 输入的字符是替换字符
    // 此时：
    // ss1.str() = hello world
    // ss2.str() = worldhi
    cout << ss1.str() << endl;
    cout << ss2.str() << endl;
    return 0;
}
~~~

```c++
ostringstream ss("1 2 3 4 ", std::ios_base::ate);	// append 方式追加 防止被<<替换
```



### 修改ss中缓存的内容

~~~c++
#include<iostream>
#include<sstream>
using namespace std;

signed main() {
	stringstream ss1("hello world");
	cout << ss1.str() << endl;
	// output: hello world
	ss1.str("");
	cout << ss1.str() << endl;  
	// output:
	ss1.str("good world");
	cout << ss1.str() << endl;
	// output: good world
    return 0;
}
~~~



### 去除字符串空格

~~~c++
#include<iostream>
#include<sstream>
using namespace std;

signed main() {

    stringstream ss("hello string and stringstream");
    cout << ss.str() << endl << endl;

    string str;
    // 注意： stringstream 是一个单词一个单词 "流入" string 的
    while (ss >> str)
    {
        cout << str << endl;
    }

    return 0;
}
~~~



### 分割字符串

~~~c++
#include<iostream>
#include<sstream>
using namespace std;

signed main() {

	string line;
	getline(cin, line);

	stringstream ss;
	ss << line;
	
	string i;
	while (getline(ss, i, ',')) {
		cout << i << endl;
	}

    return 0;
}
~~~



### 字符切片

~~~
#include<iostream>
#include<sstream>
using namespace std;

signed main() {

	string a = "hello";
	cout << a.substr(1) << endl;

    return 0;
}
~~~



### 类型转换

#### num to string

~~~c++
#include<iostream>
#include<sstream>
using namespace std;

signed main() {

	int num = 666;
	stringstream ss;
	ss << num;
	string snum;
	ss >> snum;
	cout << snum << endl;

    return 0;
}
~~~



#### string to num

~~~c++
#include<iostream>
#include<sstream>
using namespace std;

signed main() {

	string snum = "666";
	stringstream ss;
	ss << snum;
	int num;
	ss >> num;
	cout << num + 1 << endl;

    return 0;
}
~~~



### 案例



#### 统计单词数

~~~c++
#include <iostream>
#include <sstream>
#include <string>
 
using namespace std;
 
int main() {
	string str = "hello world c plus plus";
	int count = 0;
	stringstream ss(str);
	string word;
	while (ss >> word)
		count++;
	cout << count << endl;
 
	system("pause");
	return 0;
}
~~~



#### 反转单词

~~~c++
class Solution {
public:
    string reverseWords(string s) 
    {
         string res,temp;
         stringstream ss(s);
         while(ss>>temp)
         {
            res = temp + " " + res;
         }
         if(!res.empty())
         {
            res.pop_back();
         }
         return res;
    }
};
~~~



## Algorithm



# lower_bound / upper_bound

- 参考：[【C++】 详解 lower_bound 和 upper_bound 函数（看不懂来捶我！！！）_lowerbound和upperbound-CSDN博客](https://blog.csdn.net/weixin_45031801/article/details/137544229)

- 作用：有序的情况下，lower_bound返回指向第一个值不小于 / 不大于 val 的位置，也就是返回第一个大于等于val值的位置。（通过二分查找）

- 原理：二分查找

- 构造函数

  - ```c++
    template <class ForwardIterator, class T>
    ForwardIterator lower_bound (ForwardIterator first, ForwardIterator last,  const T& val);
    
    template <class ForwardIterator, class T, class Compare>
    ForwardIterator lower_bound (ForwardIterator first, ForwardIterator last, const T& val, Compare comp);
    ```

  - ForwardIterator就是一个迭代器，vector< int > v，v数组的首元素就是 v.begin()

  - T&val , 就是一个T类型的变量

  - Compare 就是一个比较器，可以传仿函数对象，也可以传函数指针







