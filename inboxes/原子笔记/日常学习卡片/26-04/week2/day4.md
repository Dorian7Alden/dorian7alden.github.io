## 2026-04-08 星期四







### 第 37 场 蓝桥·算法入门赛

> [第 37 场 蓝桥·算法入门赛](https://www.lanqiao.cn/oj-contest/newbie-37/)





#### 探究子序列【算法赛】

> https://www.lanqiao.cn/problems/21503/learning/?contest_id=298

【贪心】【栈】

- 把 string 类型，当作栈来处理。

- 考虑临界条件。

```c++
#include<iostream>
#include<string>
using namespace std;
int main()
{
    ios::sync_with_stdio(0);
    cin.tie(0);
    int n,k;
    string s,res;
    cin>>n>>k>>s;
    for(char c:s)//遍历原数
    {
        while(k>0&&!res.empty()&&c>res.back())//只要同时满足有剩余删除次数，当前遍历的数比答案最后一个数大，且你的答案里至少有一个数，就删除
        {
            res.pop_back();
            k--;//次数减1
        }
        res.push_back(c);//如果当前遍历的数比答案最后一个数大，直接读入答案，不做删除，故次数不变
    }
    if(k>0)//遍历完，还剩余删除次数
    {
        res.resize(res.size()-k);//对应文字解析最后一句话
    }
    cout<<res<<endl;
}
```



#### 【典型例题】耐力挑战【算法赛】

> https://www.lanqiao.cn/problems/21501/learning/?contest_id=298

【贪心】【反悔】【大堆根】【优先队列】

- 自己组织数据结构。struct
- 自定义 cmp 方式
- 优先队列的使用
- 大堆根，反悔消耗最大的任务，踢出去。累计消耗不超过，不在乎顺序，当前这次没超过，即可保证每次都没超过。

```C++
#include <iostream>
#include <algorithm>
#include <queue>
using namespace std;

struct task {
  int a; int b; int e;
};

bool cmp(task t1, task t2) {
  return t1.e < t2.e;
}

int main()
{
  const int N = 1e5+20;
  int n;
  cin >> n;
  task tk[N];

  for (int i=0; i<n; ++i) {
    cin >> tk[i].a >> tk[i].b;
    tk[i].e = tk[i].a + tk[i].b;
  }

  sort(tk, tk+n, cmp);

  priority_queue<int> pq;
  int x=0;

  for (int i=0; i<n; ++i) {
    x+=tk[i].a;
    pq.push(tk[i].a);
    if (x>tk[i].e) {
      x-=pq.top();
      pq.pop();
    }
  }

  cout << pq.size() << endl;
  return 0;
}
```









