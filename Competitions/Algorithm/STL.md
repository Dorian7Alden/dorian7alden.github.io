## vector

| 函数        | 作用                                     | 参数                         |
| ----------- | ---------------------------------------- | ---------------------------- |
| push_back() | 末尾添加元素                             | element                      |
| pop_back()  | 末尾删除元素                             | void                         |
| size()      | 获取元素个数                             | void                         |
| clear()     | 清空元素                                 | void                         |
| insert()    | 指定未知插入元素                         | .begin()+index, element      |
| erase()     | 删除指定未知元素，删除[a, b)区间内的元素 | .begin()+index \|\| from, to |

​	

---



## set

只能通过迭代器访问

| 函数     | 作用                   | 参数                              |
| -------- | ---------------------- | --------------------------------- |
| insert() | 插入元素               | element                           |
| find()   | 查找元素，返回迭代器   | element                           |
| erase()  | 同vector，结合find使用 | element[O(n)] \|\| iterator[O(1)] |
| size()   | 获取元素个数           | void                              |

 

---



## string

| 方法                            | 返回值类型   |
| ------------------------------- | ------------ |
| .length()                       | int          |
| .find(char\|string, startIndex) | index \| -1  |
| reverse(begin, end)             | string       |
| .substr(startIndex, lenCnt)     | string       |
| .append(string) \| +=           | string       |
| .compare(string) \| 逻辑判断符  | 0 \| 1 \| -1 |



---



## map

| 方法                                         | 返回值类型         |
| -------------------------------------------- | ------------------ |
| .size()                                      | int                |
| .clear()                                     |                    |
| .count()                                     | boolean \| (0, 1)  |
| .empty()                                     | boolean \| (0 , 1) |
| .erase(iter \| iterFirst, iterSecond \| Key) | iter \| size_type  |
| .find(key)                                   | iter \| .end()     |
| .insert(pair) \| map[key] = value            |                    |



---



### iter遍历数据

```c++
#include <iostream>
#include <map>
using namespace std;

signed main() {
    map<int, string>stu;
    stu[100] = "zhangSan";
    stu[200] = "LiSi";
    stu[300] = "Wangleo";
    map<int, string>::iterator iter;
    for (iter = stu.begin(); iter != stu.end(); iter++) {
        cout << iter->first << " : " << iter->second << endl;
    }
    return 0;
}
```



---



## queue

| 方法         | 返回值类型 |
| ------------ | ---------- |
| .empty()     | boolean    |
| .size()      | int        |
| .front()     | value      |
| .back()      | value      |
| .push(value) |            |
| .emplace()   |            |
| .pop()       |            |
| .swap(queue) | queue      |



---



## priority_queue



---



## stack

| 方法         | 返回值类型 |
| ------------ | ---------- |
| .push(value) |            |
| .pop()       | value      |
| .top()       | value      |
| .empty()     | boolean    |
| .size()      | int        |



---



## pair

make_pair()

{}

=



---



## algorithm

|                                     |      |
| ----------------------------------- | ---- |
| max()                               |      |
| min()                               |      |
| abs() \| fabs()                     |      |
| reverse(ptrS, ptrE)                 |      |
| fill(ptrS, ptrE, value)             |      |
| sort(ptrS, ptrE)                    |      |
| swap(a, b)                          |      |
| swap_ranges(a, a+size, b)           |      |
| max_element(&, &)                   |      |
| min_element(&, &)                   |      |
| max_element(&, &) - &[0] --> 取下标 |      |

