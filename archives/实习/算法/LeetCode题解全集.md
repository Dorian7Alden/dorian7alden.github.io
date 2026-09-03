> 所有的题解，除了本人手写的外，皆来自 leetcode 官方 或 相关的题解
>





# 经验之谈

:::tips
用 vector<int> 而不用 int[N]

1. 动态大小适配题目数据规模，避免越界和内存浪费；
2. 堆内存分配，杜绝栈溢出，支持大规模数据；
3. 自带实用成员函数，代码简洁、少出错；
4. 调试友好 + 传递 / 返回方便，降低排查成本；
5. 效率足够高，完全满足竞赛时间限制。

:::





****



# Hot100




## 06. 矩阵


### 6.4 搜索二维矩阵 II


[240. 搜索二维矩阵 II - 力扣（LeetCode）](https://leetcode.cn/problems/search-a-2d-matrix-ii/?envType=study-plan-v2&envId=top-100-liked)

<details class="lake-collapse"><summary id="u0d8a19b7"><span class="ne-text">答案</span></summary><pre data-language="cpp" id="fmrv6" class="ne-codeblock language-cpp"><code>class Solution {
public:
    bool ans = false;
    void solve(int s_r, int s_c, int e_r, int e_c, int t, vector&lt;vector&lt;int&gt;&gt;&amp; mp) {
        if (s_r &gt; e_r) return;
        if (s_c &gt; e_c) return;

        for (int i=s_r; i&lt;=e_r; ++i) {
            if (t == mp[i][e_c]) {
                ans = true;
                return;
            }
            if (t &gt; mp[i][e_c]) s_r=i+1;
            else {
                e_c--; 
                break;
            }
        }
        for (int j=s_c; j&lt;=e_c; ++j) {
            if (t == mp[e_r][j]) {
                ans = true;
                return;
            }
            if (t &gt; mp[e_r][j]) s_c=j+1;
            else {
                e_r--;
                break;
            }
        }
        
        solve(s_r, s_c, e_r, e_c, t, mp);
    }
    
    bool searchMatrix(vector&lt;vector&lt;int&gt;&gt;&amp; matrix, int target) {
        int n = matrix.size();
        int m = matrix[0].size();
    
        int s_r=0, s_c = 0; // 起始坐标
        int e_r=n-1, e_c = m-1; // 终止坐标
    
        solve(s_r, s_c, e_r, e_c, target, matrix);
        return ans;
    }
};</code></pre><span id="MHvnK"></span><span id="fBqbP"></span><pre data-language="cpp" id="B4I8Y" class="ne-codeblock language-cpp"><code>class Solution {
public:
    bool searchMatrix(vector&lt;vector&lt;int&gt;&gt;&amp; matrix, int target) {
        int m = matrix.size(), n = matrix[0].size();
        int x = 0, y = n - 1;
        while (x &lt; m &amp;&amp; y &gt;= 0) {
            if (matrix[x][y] == target) {
                return true;
            }
            if (matrix[x][y] &gt; target) {
                --y;
            }
            else {
                ++x;
            }
        }
        return false;
    }
};</code></pre><p id="u307eb265" class="ne-p"><br></p></details>

<details class="lake-collapse"><summary id="u25489b19"><span class="ne-text">说明</span></summary><pre data-language="cpp" id="BNag8" class="ne-codeblock language-cpp"><code>● 这个二维矩阵连续，形状固定
● 行列都满足顺序排列。
● 解题策略：
  ○ 已经是经过排列过的数，再顺序遍历就没必要。O(n * m)
  ○ 我的初始策略是一行一行地筛，一列一列地筛，逐渐缩小范围。
    当目标数大于当前行/列的最大数时，就放弃该行/列，更新起始位置，更新结束位置。
    因为顺序排列，因此，每次更新完后一定还是一个矩阵，形状保持相同。O(n + m)
  ○ 解题完之后，发现，可以再筛选的过程中用二分法筛，而不是一个一个地比较。
    理论上来说时间复杂度应该更低。O(logn + logm)</code></pre><pre data-language="cpp" id="FDf0K" class="ne-codeblock language-cpp"><code>我们可以从矩阵 matrix 的右上角 (0,n−1) 进行搜索。
在每一步的搜索过程中，如果我们位于位置 (x,y)，
那么我们希望在以 matrix 的左下角为左下角、以 (x,y) 为右上角的矩阵中进行搜索，
即行的范围为 [x,m−1]，列的范围为 [0,y]：

● 如果 matrix[x,y]=target，说明搜索完成；
● 如果 matrix[x,y]&gt;target，由于每一列的元素都是升序排列的，那么在当前的搜索矩阵中，
所有位于第 y 列的元素都是严格大于 target 的，因此我们可以将它们全部忽略，
即将 y 减少 1；
● 如果 matrix[x,y]&lt;target，由于每一行的元素都是升序排列的，那么在当前的搜索矩阵中，
所有位于第 x 行的元素都是严格小于 target 的，因此我们可以将它们全部忽略，
即将 x 增加 1。

在搜索的过程中，如果我们超出了矩阵的边界，那么说明矩阵中不存在 target。</code></pre><pre data-language="cpp" id="xF7XK" class="ne-codeblock language-cpp"><code>答案给的解法跟我的大差不差，本质上就是直接比较每行或每列的最大数，然后结合顺序排列的特性，
缩减范围。

答案比我更优的地方在于，只用了两个变量来调整范围，更加抽象。
我的思路更加清晰，逻辑更加简单，但是代码更复杂</code></pre></details>


## 07. 链表


### 7.1 相交链表


[160. 相交链表 - 力扣（LeetCode）](https://leetcode.cn/problems/intersection-of-two-linked-lists/?envType=study-plan-v2&envId=top-100-liked)

<details class="lake-collapse"><summary id="uec6ac601"><span class="ne-text">答案</span></summary><pre data-language="cpp" id="lD7t9" class="ne-codeblock language-cpp"><code>/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    ListNode *getIntersectionNode(ListNode *headA, ListNode *headB) {

        unordered_set&lt;ListNode*&gt; s;
        ListNode* ans;
    
        ans = headA;
        while(ans != nullptr) {
            s.insert(ans);
            ans = ans-&gt;next;
        }
    
        ans = headB;
        while(ans != nullptr) {
            if (s.count(ans)) return ans;
            ans = ans-&gt;next;
        }
    
        return nullptr;
    }
};</code></pre><p id="uc344bd79" class="ne-p"><br></p><pre data-language="cpp" id="zZyu6" class="ne-codeblock language-cpp"><code>/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
 class Solution {
 public:
    ListNode *getIntersectionNode(ListNode *headA, ListNode *headB) {
        if (headA == nullptr || headB == nullptr) {
            return nullptr;
        }

        ListNode* pA = headA, *pB = headB;
        while (pA != pB) { // pA == pB就返回，两种情况：1. 相交结点（地址） 2. 都为空结点，没有相交
            pA = pA == nullptr ? headB : pA-&gt;next; // 下一个结点，或者另一个链表的头节点
            pB = pB == nullptr ? headA : pB-&gt;next;
        }
     
        return pA;
    }
 };</code></pre><p id="uf1bec094" class="ne-p"><br></p></details>
<details class="lake-collapse"><summary id="ue8e0b2b1"><span class="ne-text">说明</span></summary><ol class="ne-ol"><li id="u54fff572" data-lake-index-type="0"><span class="ne-text">比较结点的地址！不是比较值</span></li></ol></details>


### 7.2 反转链表


[206. 反转链表 - 力扣（LeetCode）](https://leetcode.cn/problems/reverse-linked-list/description/?envType=study-plan-v2&envId=top-100-liked)

<details class="lake-collapse"><summary id="u798db277"><span class="ne-text">答案</span></summary><pre data-language="cpp" id="Z3ToE" class="ne-codeblock language-cpp"><code>/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* reverseList(ListNode* head) {

        if (head == nullptr) return nullptr;
        if (head-&gt;next == nullptr) return head;
    
        ListNode* pre = nullptr;
        ListNode* next = head-&gt;next;
    
        while(head != nullptr) {
    
            if (next == nullptr) return head;
    
            ListNode* nextN = next-&gt;next;
    
            head-&gt;next = pre;
            next-&gt;next = head;
    
            pre = head;
            head = next;
            next = nextN;
        }
        return head;
    }
};</code></pre><p id="u169b9e7a" class="ne-p"><br></p><pre data-language="cpp" id="qnlkF" class="ne-codeblock language-cpp"><code>class Solution {
public:
ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    ListNode* curr = head;
    while (curr) {
        ListNode* next = curr-&gt;next;
        curr-&gt;next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}
};</code></pre><p id="u72e1091b" class="ne-p"><br></p><pre data-language="cpp" id="ae98d" class="ne-codeblock language-cpp"><code>class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        if (!head || !head-&gt;next) {
            return head;
        }
        ListNode* newHead = reverseList(head-&gt;next);
        head-&gt;next-&gt;next = head;
        head-&gt;next = nullptr;
        return newHead;
    }
};</code></pre><div data-type="tips" class="ne-alert"><p id="u3e33b4f2" class="ne-p"><span class="ne-text">思路比较复杂。从最后一个结点依次开始往前反转。O(n)的时间跟空间。递归。</span></p><ol class="ne-ol"><li id="ubc9a58e1" data-lake-index-type="0"><span class="ne-text">顺序结点中的下一个结点的下一个结点=该顺序结点。该顺序结点的下一个结点为 null，这是为了让 head 结点的下一个结点一定为 null，如果递归还没结束的话，下面的语句会覆盖这个 null</span></li><li id="ua1f13c99" data-lake-index-type="0"><span class="ne-text">然后，上面↑的该顺序结点就会成为下一个递归中的下一个结点</span></li></ol></div></details>
<details class="lake-collapse"><summary id="ue585c997"><span class="ne-text">说明</span></summary><ul class="ne-ul"><li id="ube5c022d" data-lake-index-type="0"><span class="ne-text">我的答题一次性反转了两条链。cur 的 next 跟 next 的 next</span></li></ul></details>


### 7.3 回文链表


[234. 回文链表 - 力扣（LeetCode）](https://leetcode.cn/problems/palindrome-linked-list/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    bool isPalindrome(ListNode* head) {
        
        const int N = 1e5+10;
        ListNode* arr[N];
        int cnt = 0;

        if (head == nullptr) return true;
        if (head->next == nullptr) return true;

        while (head->next) {
            arr[cnt++] = head;
            head = head->next;
        }
        arr[cnt++] = head;

        int p1 = 0, p2 = cnt-1;

        for (; p1*2 < cnt; ++p1,--p2) {
            if (arr[p1]->val != arr[p2]->val) return false;
        }

        return true;
    }
};
```

:::tips
失败的点：空间 O(n)

1. 回文链表比较的是结点的值！不是结点的内存地址。值相同但是结点不同，比较结点永远不等
2. 我的 while 循环中，没有把最后一个结点存到数组里边。注意存数据的先后逻辑
3. 没必要存储内存地址，直接存值就好了
4. 数组一般用 vector，而不是 []
5. 回文链表是对称的。不用遍历整个数组，1/2 就够了

:::



```cpp
class Solution {
public:
    bool isPalindrome(ListNode* head) {
        vector<int> vals;
        while (head != nullptr) {
            vals.emplace_back(head->val);
            head = head->next;
        }
        for (int i = 0, j = (int)vals.size() - 1; i < j; ++i, --j) {
            if (vals[i] != vals[j]) {
                return false;
            }
        }
        return true;
    }
};
```



```cpp
class Solution {
    ListNode* frontPointer;
public:
    bool recursivelyCheck(ListNode* currentNode) {
        if (currentNode != nullptr) {
            if (!recursivelyCheck(currentNode->next)) {
                return false;
            }
            if (currentNode->val != frontPointer->val) {
                return false;
            }
            frontPointer = frontPointer->next;
        }
        return true;
    }

    bool isPalindrome(ListNode* head) {
        frontPointer = head;
        return recursivelyCheck(head);
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/palindrome-linked-list/solutions/457059/hui-wen-lian-biao-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
递归的特性：

1. 先进入，再依次返回。适合做反向操作。复杂问题拆成简单问题，再变成复杂问题。
2. 递归可以用来控制遍历顺序。（树的前序，后序，中序遍历）做线性反转操作。链表在只有单向的情况下，可以利用递归的特性，实现倒序操作（可以类比栈）。
3. 递归时携带的参数有重要的作用。

:::

:::tips
解题思路：O(n)，O(n)

+ 利用递归的倒序，结合前序指针，起到前后对比的作用。

:::



```cpp
class Solution {
public:
    bool isPalindrome(ListNode* head) {
        if (head == nullptr) {
            return true;
        }

        // 找到前半部分链表的尾节点并反转后半部分链表
        ListNode* firstHalfEnd = endOfFirstHalf(head);
        ListNode* secondHalfStart = reverseList(firstHalfEnd->next);

        // 判断是否回文
        ListNode* p1 = head;
        ListNode* p2 = secondHalfStart;
        bool result = true;
        while (result && p2 != nullptr) {
            if (p1->val != p2->val) {
                result = false;
            }
            p1 = p1->next;
            p2 = p2->next;
        }

        // 还原链表并返回结果
        firstHalfEnd->next = reverseList(secondHalfStart);
        return result;
    }

    ListNode* reverseList(ListNode* head) {
        ListNode* prev = nullptr;
        ListNode* curr = head;
        while (curr != nullptr) {
            ListNode* nextTemp = curr->next;
            curr->next = prev;
            prev = curr;
            curr = nextTemp;
        }
        return prev;
    }

    ListNode* endOfFirstHalf(ListNode* head) {
        ListNode* fast = head;
        ListNode* slow = head;
        while (fast->next != nullptr && fast->next->next != nullptr) {
            fast = fast->next->next;
            slow = slow->next;
        }
        return slow;
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/palindrome-linked-list/solutions/457059/hui-wen-lian-biao-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
优化空间复杂度需要改变输入。

前两种题解没用双指针是因为：这是单向链表，在不改变结构的前提下只能单向移动

改为双指针可以优化空间，但是会改变数据结构，需要对其恢复结构。（保证该函数的原子性，并发问题）

:::

:::tips
解题思路：O(n)，O(1)

1. 找到一半结点的尾结点。快慢指针，一个移动 1，一个移动 2（注意奇数）
2. 将一半的结点反向连接
3. 双指针同时遍历，判断是否相等
4. 恢复结点连接方向

:::



### 7.4 环形链表


[141. 环形链表 - 力扣（LeetCode）](https://leetcode.cn/problems/linked-list-cycle/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    bool hasCycle(ListNode *head) {
        ListNode* p1 = head;
        ListNode* p2 = head;
        if (head == nullptr) return false;
        if (head->next == nullptr) return false;

        while (p1 != nullptr) {
            if (p2 != nullptr) p2 = p2->next;
            if (p2 != nullptr) p2 = p2->next;
            p1 = p1->next;
            if (p1 == p2 && p2 != nullptr) return true;
        }
        return false;
    }
};
```

:::tips
快慢指针。如果有环，快指针一定会与满指针相遇。

:::



```cpp
class Solution {
public:
    bool hasCycle(ListNode *head) {
        unordered_set<ListNode*> seen;
        while (head != nullptr) {
            if (seen.count(head)) {
                return true;
            }
            seen.insert(head);
            head = head->next;
        }
        return false;
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/linked-list-cycle/solutions/440042/huan-xing-lian-biao-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
O(n) O(n)

如果有环，则一定会有重复的结点，通过哈希表去重，如果有重复，则判断为有环

:::



```cpp
class Solution {
public:
    bool hasCycle(ListNode* head) {
        if (head == nullptr || head->next == nullptr) {
            return false;
        }
        ListNode* slow = head;
        ListNode* fast = head->next;
        while (slow != fast) {
            if (fast == nullptr || fast->next == nullptr) {
                return false;
            }
            slow = slow->next;
            fast = fast->next->next;
        }
        return true;
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/linked-list-cycle/solutions/440042/huan-xing-lian-biao-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
O(N) O(1)

快指针如果为 null，则没有环。

<font style="color:rgb(38, 38, 38);background-color:rgb(240, 240, 240);">当链表中存在环时，每一轮移动后快慢指针距离减小一。而初始距离为环的长度，因此至多移动 N 轮.</font>

:::



### 7.5 环形链表 II


[142. 环形链表 II - 力扣（LeetCode）](https://leetcode.cn/problems/linked-list-cycle-ii/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    ListNode *detectCycle(ListNode *head) {
        if (head == nullptr) return nullptr;
        unordered_set<ListNode*> s;
        ListNode* ans = head;

        while (ans->next != nullptr) {
            if (s.count(ans)) return ans;
            s.insert(ans);
            ans = ans->next;
        }
        return nullptr;
    }
};
```

:::tips
O(n) O(n) 哈希表，有重复结点直接返回

:::



```cpp
class Solution {
public:
    ListNode *detectCycle(ListNode *head) {
        unordered_set<ListNode *> visited;
        while (head != nullptr) {
            if (visited.count(head)) {
                return head;
            }
            visited.insert(head);
            head = head->next;
        }
        return nullptr;
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/linked-list-cycle-ii/solutions/441131/huan-xing-lian-biao-ii-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```



```cpp
class Solution {
public:
    ListNode *detectCycle(ListNode *head) {
        ListNode *slow = head, *fast = head;
        while (fast != nullptr) {
            slow = slow->next;
            if (fast->next == nullptr) {
                return nullptr;
            }
            fast = fast->next->next;
            if (fast == slow) {
                ListNode *ptr = head;
                while (ptr != slow) {
                    ptr = ptr->next;
                    slow = slow->next;
                }
                return ptr;
            }
        }
        return nullptr;
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/linked-list-cycle-ii/solutions/441131/huan-xing-lian-biao-ii-by-leetcode-solution/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
O(N) O(1)

通过数学表达式推算入环位置。额外加入一个指针与 slow 指针配合，移动到入环位置。

算法竞赛不推荐去推理数学表达式。实习推荐推理一下过程

结论：因此，当发现 slow 与 fast 相遇时，我们再额外使用一个指针 ptr。起始，它指向链表头部；随后，它和 slow 每次向后移动一个位置。最终，它们会在入环点相遇。

:::



### 7.6 合并两个有序链表


[21. 合并两个有序链表 - 力扣（LeetCode）](https://leetcode.cn/problems/merge-two-sorted-lists/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {
        ListNode dummy(0);
        ListNode* curr = &dummy;
        
        while (list1 && list2) {
            if (list1->val <= list2->val) {
                curr->next = list1;
                list1 = list1->next;
            } else {
                curr->next = list2;
                list2 = list2->next;
            }
            curr = curr->next;
        }
        
        curr->next = list1 ? list1 : list2;
        return dummy.next;
    }
};
```

:::tips
O(N) O(1)

概念模糊：改变指针 || 改变连接关系

+ 改变指针：list1 = ... 是改变指针的指向，不影响连接关系
+ 改变连接：list->next = ... 改变了连接关系

:::



```cpp
class Solution {
public:
    ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
        if (l1 == nullptr) {
            return l2;
        } else if (l2 == nullptr) {
            return l1;
        } else if (l1->val < l2->val) {
            l1->next = mergeTwoLists(l1->next, l2);
            return l1;
        } else {
            l2->next = mergeTwoLists(l1, l2->next);
            return l2;
        }
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/merge-two-sorted-lists/solutions/226408/he-bing-liang-ge-you-xu-lian-biao-by-leetcode-solu/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
O(n+m) O(n+m)

取最小的头结点与下一个循环拼接。下一个循环又会取最小的头结点与下下个循环拼接。

$ \left \{
    \begin{matrix}
list1[0]+merge(list1[1:],list2) & list1[0]<list2[0] \\
list2[0]+merge(list1,list2[1:]) & otherwise \\
    \end{matrix}
\right . $

:::



```cpp
\class Solution {
public:
    ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
        ListNode* preHead = new ListNode(-1);

        ListNode* prev = preHead;
        while (l1 != nullptr && l2 != nullptr) {
            if (l1->val < l2->val) {
                prev->next = l1;
                l1 = l1->next;
            } else {
                prev->next = l2;
                l2 = l2->next;
            }
            prev = prev->next;
        }

        // 合并后 l1 和 l2 最多只有一个还未被合并完，我们直接将链表末尾指向未合并完的链表即可
        prev->next = l1 == nullptr ? l2 : l1;

        return preHead->next;
    }
};

作者：力扣官方题解
链接：https://leetcode.cn/problems/merge-two-sorted-lists/solutions/226408/he-bing-liang-ge-you-xu-lian-biao-by-leetcode-solu/
来源：力扣（LeetCode）
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
```

:::tips
O(n+m) O(1)

:::



### 7.7 两数相加


[2. 两数相加 - 力扣（LeetCode）](https://leetcode.cn/problems/add-two-numbers/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode* dummy = new ListNode(0);
        ListNode* curr = dummy;
        int carry = 0;

        while (l1 != nullptr || l2 != nullptr || carry != 0) {
            int val1 = (l1 != nullptr) ? l1->val : 0;
            int val2 = (l2 != nullptr) ? l2->val : 0;
            
            int sum = val1 + val2 + carry;
            int current_val = sum % 10;
            carry = sum / 10;

            curr->next = new ListNode(current_val);
            curr = curr->next;

            if (l1 != nullptr) l1 = l1->next;
            if (l2 != nullptr) l2 = l2->next;
        }

        ListNode* result = dummy->next;
        delete dummy;
        return result;
    }
};
```

```cpp
while (l1 != nullptr || l2 != nullptr || carry != 0) 只要不为空就得继续操作
巧用 % / 进行进位时操作。% 进位后剩多少， / 进位值多少
当为空时，给一个默认值，三则运算符非常方便。 ? a : b 。用来保底
哨兵结点
```



### 7.8 删除链表的倒数第 N 个结点


[19. 删除链表的倒数第 N 个结点 - 力扣（LeetCode）](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/description/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* removeNthFromEnd(ListNode* head, int n) {
        if (head == nullptr) return nullptr;
        vector<ListNode*> arr;

        while (head != nullptr) {
            arr.push_back(head);
            head = head->next;
        }

        int size = arr.size();
        if (size == 1) return nullptr;
        int to = size - n;
        if (to == 0) {
            delete arr[to];
            return arr[to+1];
        }
        else {
            arr[to-1]->next = arr[to]->next;
            delete arr[to];
            return arr[0];
        }
    }
};
```

```cpp
用一个数组存下每一个结点
删除哪个，就删哪个
```

```cpp
class Solution {
public:
    ListNode* removeNthFromEnd(ListNode* head, int n) {
        ListNode* dummy = new ListNode(0, head);
        ListNode* first = head;
        ListNode* second = dummy;
        for (int i = 0; i < n; ++i) {
            first = first->next;
        }
        while (first) {
            first = first->next;
            second = second->next;
        }
        second->next = second->next->next;
        ListNode* ans = dummy->next;
        delete dummy;
        return ans;
    }
};
```

```cpp
当特征出现：有两个固定的点是，可以考虑用双指针
这道题中有两个固定点，前后距离始终一直，末尾结点，跟倒数第 n 个结点，距离为 n 。
即用距离为 n 的快慢指针，当快指针停止时，即结束。

```



### 7.9 两两交换链表中的结点


[24. 两两交换链表中的节点 - 力扣（LeetCode）](https://leetcode.cn/problems/swap-nodes-in-pairs/?envType=study-plan-v2&envId=top-100-liked)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        
        ListNode* dummy = new ListNode;
        dummy->next = head;
        ListNode* cur = head;
        ListNode* pre = dummy;

        while (cur && cur->next) {

            pre->next = cur->next;
            cur->next = pre->next->next;
            pre->next->next = cur;

            pre = cur;
            cur = cur->next;
        }

        return dummy->next;
    }
};
```

```cpp
给一个哨兵结点放在 head 的前面，快速返回首节点。
用两个结点完成遍历交换，一个 pre 结点，一个 cur 结点，两两模拟交换流程即可。
当没有两个有效结点时，就不用交换，即可结束
```

```cpp
// 妙在不用额外定义首节点，先将循环过程打开以后，再返回到最初的结点，即为首节点。
// 写起来稍麻烦，不直观，相对更加抽象

class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        if (head == nullptr || head->next == nullptr) {
            return head;
        }
        ListNode* newHead = head->next;
        head->next = swapPairs(newHead->next);
        newHead->next = head;
        return newHead;
    }
};
```



### 7.10 **<font style="color:rgb(26, 26, 26);">K 个一组翻转链表</font>**


[K 个一组翻转链表](https://leetcode.cn/problems/reverse-nodes-in-k-group/)



```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        ListNode* dummy = new ListNode(0);
        dummy->next = head;
        // 主函数的前驱节点：始终指向待翻转分组的前一个节点（不可改名，核心锚点）
        ListNode* pre = dummy;

        while (true) {
            // 1. 找待翻转分组的尾节点tail，走k步判断是否够数
            ListNode* tail = pre;
            for (int i = 0; i < k; ++i) {
                tail = tail->next;
                if (tail == nullptr) return dummy->next; // 不足k个，直接返回
            }

            // 2. 保存关键节点，避免翻转丢失链表
            ListNode* start = pre->next;    // 待翻转分组的头
            ListNode* next_group = tail->next;  // 下一组的头

            ListNode* pre_node = nullptr;
            ListNode* cur = start;
            ListNode* next = nullptr;
            // 终止条件：pre_node指向tail时，整个区间翻转完成
            while (pre_node != tail) {
                next = cur->next; // 先保存下一个节点，防止丢失
                cur->next = pre_node;  // 翻转当前节点指针
                // 指针后移，继续翻转下一个节点
                pre_node = cur;
                cur = next;
            }
            // 3. 拼接翻转后的链表，重新连接
            pre->next = tail;         // 前驱指向翻转后的分组头（原tail）
            start->next = next_group; // 翻转后的分组尾（原start）指向下一组
            // 4. 更新前驱节点，处理下一组
            pre = start;
        }

        return dummy->next; // 理论上不会走到，循环内已有return
    }
};
```

```cpp
我的思路：
- 分批次处理。先遍历下一个组的结点长度，是否满足。
- 满足之后，借用遍历到的首节点，尾结点，先进行首尾地连接
- 然后才是批次的内部翻转

问题：
- 思路不清晰。一个变量多个含义，在上个批次中的含义跟下个批次中的含义难以对应。细节比较多，导致没有设计好。
- 循环过程中，没有注重临界情况。
- 空指针异常。
```

```cpp
class Solution {
public:
    // 翻转一个子链表，并且返回新的头与尾
    pair<ListNode*, ListNode*> myReverse(ListNode* head, ListNode* tail) {
        ListNode* prev = tail->next;
        ListNode* p = head;
        while (prev != tail) {
            ListNode* nex = p->next;
            p->next = prev;
            prev = p;
            p = nex;
        }
        return {tail, head};
    }

    ListNode* reverseKGroup(ListNode* head, int k) {
        ListNode* hair = new ListNode(0);
        hair->next = head;
        ListNode* pre = hair;

        while (head) {
            ListNode* tail = pre;
            // 查看剩余部分长度是否大于等于 k
            for (int i = 0; i < k; ++i) {
                tail = tail->next;
                if (!tail) {
                    return hair->next;
                }
            }
            ListNode* nex = tail->next;
            // 这里是 C++17 的写法，也可以写成
            // pair<ListNode*, ListNode*> result = myReverse(head, tail);
            // head = result.first;
            // tail = result.second;
            tie(head, tail) = myReverse(head, tail);
            // 把子链表重新接回原链表
            pre->next = head;
            tail->next = nex;
            pre = tail;
            head = tail->next;
        }

        return hair->next;
    }
};
```



### 7.11 随机链表的复制


[138. 随机链表的复制 - 力扣（LeetCode）](https://leetcode.cn/problems/copy-list-with-random-pointer/description/?envType=study-plan-v2&envId=top-100-liked)

```cpp
/*
// Definition for a Node.
class Node {
public:
    int val;
    Node* next;
    Node* random;
    
    Node(int _val) {
        val = _val;
        next = NULL;
        random = NULL;
    }
};
*/

class Solution {
public:
    unordered_map<Node*, Node*> cachedNode;

    Node* copyRandomList(Node* head) {
        if (head == nullptr) return nullptr;
        if (!cachedNode.count(head)) {
            Node* headNew = new Node(head->val);
            cachedNode[head] = headNew;
            headNew->next = copyRandomList(head->next);
            headNew->random = copyRandomList(head->random);
        }
        return cachedNode[head];
    }
};
```

```cpp
class Solution {
public:
    Node* copyRandomList(Node* head) {
        if (head == nullptr) {
            return nullptr;
        }
        for (Node* node = head; node != nullptr; node = node->next->next) {
            Node* nodeNew = new Node(node->val);
            nodeNew->next = node->next;
            node->next = nodeNew;
        }
        for (Node* node = head; node != nullptr; node = node->next->next) {
            Node* nodeNew = node->next;
            nodeNew->random = (node->random != nullptr) ? node->random->next : nullptr;
        }
        Node* headNew = head->next;
        for (Node* node = head; node != nullptr; node = node->next) {
            Node* nodeNew = node->next;
            node->next = node->next->next;
            nodeNew->next = (nodeNew->next != nullptr) ? nodeNew->next->next : nullptr;
        }
        return headNew;
    }
};
```

:::tips
不是很懂过程

:::





## 08. 二叉树








### 8.3 翻转二叉树  
#### 题目：
给你一棵二叉树的根节点 `root` ，翻转这棵二叉树，并返回其根节点。

**示例 1：**

![image-20260830154049614](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154049614.png)

```plain
输入：root = [4,2,7,1,3,6,9]
输出：[4,7,2,9,6,3,1]
```

**示例 2：**

![image-20260830154104216](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154104216.png)



```plain
输入：root = [2,1,3]
输出：[2,3,1]
```

**示例 3：**

```plain
输入：root = []
输出：[]
```

**提示：**

+ 树中节点数目范围在 `[0, 100]` 内
+ `-100 <= Node.val <= 100`

#### 题解：
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    TreeNode* invertTree(TreeNode* root) {
        if(root==nullptr) return nullptr;
        auto l = invertTree(root->left);
        auto r = invertTree(root->right);
        auto tmp = l;
        root->left = r;
        root->right = tmp;
        return root;
    }
};
```

**启发：**

+ 一个函数直接递归。从底层到表层的思维。先考虑最底层的状态，交换左右两个子树，然后返回根结点，然后依次往上走，再考虑遍历顺序。
+ 核心代码在递归代码的下面。（先进到地下再从底下执行回到顶上）



### 8.4 对称二叉树  
#### 题目：
给你一个二叉树的根节点 `root` ， 检查它是否轴对称。

**示例 1：**

![image-20260830154116449](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154116449.png)



```plain
输入：root = [1,2,2,3,4,4,3]
输出：true
```

**示例 2：**

![image-20260830154127914](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154127914.png)



```plain
输入：root = [1,2,2,null,3,null,3]
输出：false
```

**提示：**

+ 树中节点数目在范围 `[1, 1000]` 内
+ `-100 <= Node.val <= 100`

**进阶：**你可以运用递归和迭代两种方法解决这个问题吗？

#### 题解：（递归）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
   bool recur(TreeNode* L, TreeNode* R){
        if(L==nullptr && R==nullptr) return true;
        if(L== nullptr || R==nullptr || L->val != R->val) return false;
        return recur(L->left,R->right) && recur(L->right,R->left);
   }

public:
    bool isSymmetric(TreeNode* root) {
       if(root==nullptr) return true;
       return recur(root->left, root->right);
    }
};
```

#### 题解：（迭代）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    bool isSymmetric(TreeNode* root) {
        if (!root) return true; // 空树是对称的

        queue<TreeNode*> q;
        q.push(root->left);
        q.push(root->right);

        while (!q.empty()) {
            TreeNode* leftNode = q.front(); q.pop();
            TreeNode* rightNode = q.front(); q.pop();

            // 两个都为空，继续比较下一对
            if (!leftNode && !rightNode) continue;
            // 一个为空一个不为空，不对称
            if (!leftNode || !rightNode) return false;
            // 值不相等，不对称
            if (leftNode->val != rightNode->val) return false;

            // 按镜像顺序入队
            q.push(leftNode->left);
            q.push(rightNode->right);
            q.push(leftNode->right);
            q.push(rightNode->left);
        }
        return true;
    }
};
```

**启发：**

+ **递归**：函数**自己调用自己**，隐式地利用了**函数调用栈**来保存状态。
+ **迭代**：用**循环**显式地控制执行流程，通常会使用**栈、队列、数组**等数据结构来保存需要处理的中间状态。
+ 迭代，先保存结点，再慢慢地去判断是否合法。



### 8.5 **二叉树的直径**
#### 题目：
给你一棵二叉树的根节点，返回该树的 **直径** 。

二叉树的 **直径** 是指树中任意两个节点之间最长路径的 **长度** 。这条路径可能经过也可能不经过根节点 `root` 。

两节点之间路径的 **长度** 由它们之间边数表示。

**示例 1：**

![image-20260830154142379](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154142379.png)



```plain
输入：root = [1,2,3,4,5]
输出：3
解释：3 ，取路径 [4,2,1,3] 或 [5,2,1,3] 的长度。
```

**示例 2：**

```plain
输入：root = [1,2]
输出：1
```

**提示：**

+ 树中节点数目在范围 `[1, 104]` 内
+ `-100 <= Node.val <= 100`

#### 题解：
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
    int ans;
    int depth(TreeNode* rt){
        if (rt == NULL) { return 0; } // 访问到空节点了，返回0
        int L = depth(rt->left); // 左儿子为根的子树的深度
        int R = depth(rt->right); // 右儿子为根的子树的深度
        ans = max(ans, L + R + 1); // 计算d_node即L+R+1 并更新ans
        return max(L, R) + 1; // 返回该节点为根的子树的深度
    }
public:
    int diameterOfBinaryTree(TreeNode* root) {
        ans = 1;
        depth(root);
        return ans - 1;
    }
```

**启发：**

+ 直径 = 结点数 - 1
+ 返回值不为void的遍历。 
    - 需要搞清楚返回数据的意义。
    - 遍历过程中，可以用变量储存子遍历的结果，进行处理。
    - 两个重要的点：返回值意义。中间处理的意义。



### 8.6 二叉树的层序遍历
#### 题目：
给你二叉树的根节点 `root` ，返回其节点值的 **层序遍历** 。 （即逐层地，从左到右访问所有节点）。

**示例 1：**

![image-20260830154152622](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154152622.png)



```plain
输入：root = [3,9,20,null,null,15,7]
输出：[[3],[9,20],[15,7]]
```

**示例 2：**

```plain
输入：root = [1]
输出：[[1]]
```

**示例 3：**

```plain
输入：root = []
输出：[]
```

**提示：**

+ 树中节点数目在范围 `[0, 2000]` 内
+ `1000 <= Node.val <= 1000`

#### 题解：
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    vector<vector<int>> levelOrder(TreeNode* root) {
        vector<vector<int>> ans;
        if (!root) return ans; // 空树直接返回

        queue<TreeNode*> q;
        q.push(root);

        while (!q.empty()) {
            int levelSize = q.size(); // 当前层的节点数
            vector<int> line;

            for (int i = 0; i < levelSize; i++) {
                TreeNode* node = q.front(); // 取队首
                q.pop();                    // 弹出队首
                line.emplace_back(node->val);

                if (node->left)  q.push(node->left);
                if (node->right) q.push(node->right);
            }

            ans.emplace_back(line); // 把当前层的结果加入答案
        }

        return ans;
    }
};
```

### 8.7 将有序数组转换为二叉搜索树
#### 题目：
给你一个整数数组 `nums` ，其中元素已经按 **升序** 排列，请你将其转换为一棵 平衡 二叉搜索树。

**示例 1：**

![image-20260830154206002](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154206002.png)



```plain
输入：nums = [-10,-3,0,5,9]
输出：[0,-3,9,-10,null,5]
解释：[0,-10,5,null,-3,null,9] 也将被视为正确答案：
```

![image-20260830154217390](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154217390.png)



**示例 2：**

![image-20260830154234301](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154234301.png)



```plain
输入：nums = [1,3]
输出：[3,1]
解释：[1,null,3] 和 [3,1] 都是高度平衡二叉搜索树。
```

**提示：**

+ `1 <= nums.length <= $10^4$`
+ `$-10^4$ <= nums[i] <= $10^4$`
+ `nums` 按 **严格递增** 顺序排列

#### 题解：
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:

    TreeNode* dfs(vector<int>& nums, int l, int r) {
        if (l > r) return nullptr;

        int m = l + (r - l) / 2;
        TreeNode* root = new TreeNode(nums[m]);
        root->left = dfs(nums, l, m-1);
        root->right = dfs(nums, m+1, r);

        return root;
    }

    TreeNode* sortedArrayToBST(vector<int>& nums) {
        return dfs(nums, 0, nums.size()-1);
    }
};
```

**启发：**

+ 升序排列，用中序遍历。
+ 依次取数组中的中间的树为双亲结点，一定能保证该二叉树为平衡二叉搜索树。（证明过程见 **1382. 将二叉搜索树变平衡**）

### 8.8 验证二叉搜索树
#### 题目：
给你一个二叉树的根节点 `root` ，判断其是否是一个有效的二叉搜索树。

**有效** 二叉搜索树定义如下：

+ 节点的左只包含 **严格小于** 当前节点的数。

子树

+ 节点的右子树只包含 **严格大于** 当前节点的数。
+ 所有左子树和右子树自身必须也是二叉搜索树。

**示例 1：**

![image-20260830154247424](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154247424.png)

```plain
输入：root = [2,1,3]
输出：true
```

**示例 2：**

![image-20260830154253624](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154253624.png)

```plain
输入：root = [5,1,4,null,null,3,6]
输出：false
解释：根节点的值是 5 ，但是右子节点的值是 4 。
```

**提示：**

+ 树中节点数目范围在`[1, 104]` 内
+ `$-2^{31}$ <= Node.val <= $2^{31}$ - 1`

#### 题解：
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    bool isValidBST(TreeNode* root) {
        return isValidBST(root, LLONG_MIN, LLONG_MAX);
    }
    
private:
    bool isValidBST(TreeNode* node, long long minVal, long long maxVal) {
        if (!node) return true;
        
        // 如果当前节点值超出范围，则不是BST
        if (node->val <= minVal || node->val >= maxVal) return false;
        
        // 递归检查左右子树，并更新范围
        return isValidBST(node->left, minVal, node->val) && 
               isValidBST(node->right, node->val, maxVal);
    }
};
```

**启发：**

+ 遍历的时候，注意前后两个状态的区别。是否携带上一个遍历的信息。更新遍历状态。`minVal` 与`maxVal` 。

### 8.9 二叉搜索树中第 K 小的元素
#### 题目：
给定一个二叉搜索树的根节点 `root` ，和一个整数 `k` ，请你设计一个算法查找其中第 `k` ****小的元素（从 1 开始计数）。

**示例 1：**

![image-20260830154302525](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154302525.png)

```plain
输入：root = [3,1,4,null,2], k = 1
输出：1
```

**示例 2：**

![image-20260830154308776](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154308776.png)

```plain
输入：root = [5,3,6,2,4,null,null,1], k = 3
输出：3
```

**提示：**

+ 树中的节点数为 `n` 。
+ `1 <= k <= n <= $10^4$`
+ `0 <= Node.val <= $10^4$`

**进阶：**如果二叉搜索树经常被修改（插入/删除操作）并且你需要频繁地查找第 `k` 小的值，你将如何优化算法？

#### 题解：（递归）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    int ans = -1;
    int kk;
    void dfs(TreeNode* root) {
        if (root == nullptr) return;
        dfs(root->left);
        if (kk > 0) {
            ans = root->val;
            kk--;
        }
        if (kk > 0) dfs(root->right);
    }

    int kthSmallest(TreeNode* root, int k) {
        kk = k;
        dfs(root);
        return ans;
    }
};
```

**启发：**

+ 执行语句如果需要判断零界值的话，直接固定true的条件执行该语句。如 `if (kk>0) { ... }` 所示，只有在特定条件下才执行，减少复杂度，减少误判。而不是如下所示的多次判断：

```cpp
void dfs(TreeNode* root) {
        if (root == nullptr || kk <= 0) return;
        dfs(root->left);
        if (root == nullptr || kk <= 0) return;
        ans = root->val;
        kk--;
        if (kk<=0) return;
        else dfs(root->right);
    }
```

#### 题解：（迭代）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    int kthSmallest(TreeNode* root, int k) {
        stack<TreeNode*> st;
        TreeNode* cur = root;

        while (cur != nullptr || !st.empty()) {
            while (cur) {
                st.push(cur);
                cur = cur->left;
            }
            cur = st.top();
            st.pop();
            --k;
            if (k <= 0) return cur->val;
            cur = cur->right;
        }
        return -1;
    }
};
```

**启发：**

+ 迭代的思路：先把每个循环的起点扔到栈里面去，然后按照顺序依次遍历。
+ 因为中序遍历的特性，先把所有左子树依次从顶层往底层扔到栈里面储存，先进后出，跟递归一样。然后是遍历栈里面所有的左子树，把左子树取出来，先取值进行操作，再查看右子树的情况，然后该左子树结束，轮到下次遍历。
+ 迭代相当于是把整个中序遍历拆成了遍历所有的左子树这一种情况，先后顺序由栈解决。

### 8.10 二叉树的右视图
#### 题目：
给定一个二叉树的 **根节点** `root`，想象自己站在它的右侧，按照从顶部到底部的顺序，返回从右侧所能看到的节点值。

**示例 1：**

**输入：**root = [1,2,3,null,5,null,4]

**输出：**[1,3,4]

**解释：**

![image-20260830154319860](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154319860.png)

**示例 2：**

**输入：**root = [1,2,3,4,null,null,null,5]

**输出：**[1,3,4,5]

**解释：**

![image-20260830154327247](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154327247.png)

**示例 3：**

**输入：**root = [1,null,3]

**输出：**[1,3]

**示例 4：**

**输入：**root = []

**输出：**[]

**提示:**

+ 二叉树的节点个数的范围是 `[0,100]`
+ `-100 <= Node.val <= 100`

#### 题解：
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:

    vector<int> rightSideView(TreeNode* root) {
        if (root == nullptr) return vector<int>();
        vector<int> ans;
        queue<TreeNode*> q;
        q.push(root);

        while (!q.empty()) {
            int size = q.size();
            ans.emplace_back(q.back()->val);

            for (int i=0; i<size; i++) {
                TreeNode* f = q.front();q.pop();
                if (f->left) q.push(f->left);
                if (f->right) q.push(f->right);
            }
        }
        return ans;
    }
};
```

**启发：**

+ 用队列存储结点数据，层序遍历。
+ while是遍历每层的所有结点。一批一批（一层一层）的遍历

### 8.11 二叉树展开为链表
#### 题目：
给你二叉树的根结点 `root` ，请你将它展开为一个单链表：

+ 展开后的单链表应该同样使用 `TreeNode` ，其中 `right` 子指针指向链表中下一个结点，而左子指针始终为 `null` 。
+ 展开后的单链表应该与二叉树 [先序遍历](https://baike.baidu.com/item/%E5%85%88%E5%BA%8F%E9%81%8D%E5%8E%86/6442839?fr=aladdin) 顺序相同。

**示例 1：**

![image-20260830154335319](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154335319.png)

```plain
输入：root = [1,2,5,3,4,null,6]
输出：[1,null,2,null,3,null,4,null,5,null,6]
```

**示例 2：**

```plain
输入：root = []
输出：[]
```

**示例 3：**

```plain
输入：root = [0]
输出：[0]
```

**提示：**

+ 树中结点数在范围 `[0, 2000]` 内
+ `-100 <= Node.val <= 100`

**进阶：**你可以使用原地算法（`O(1)` 额外空间）展开这棵树吗？

#### 题解：（队列）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    void flatten(TreeNode* root) {
        if (!root) return;

        queue<TreeNode*> q;
        preorder(root, q); 

        TreeNode* prev = q.front();
        q.pop();
        prev->left = nullptr;

        while (!q.empty()) {
            TreeNode* cur = q.front();
            q.pop();
            prev->right = cur;
            cur->left = nullptr;
            prev = cur;
        }
    }

    void preorder(TreeNode* node, queue<TreeNode*>& q) {
        if (!node) return;
        q.push(node);
        preorder(node->left, q);
        preorder(node->right, q);
    }
};
```

**启发：**

+ 处理队列链接前后两个结点的时候，先处理pre结点，再遍历到最后一个结点，最后一个结点的右指针一定为nullptr，防止难处理。
+ 一般都是先处理“头”，不管尾，对“头”做处理，提取规律覆盖尾。

#### 题解：（栈）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    void flatten(TreeNode* root) {
        if (!root) return;

        stack<TreeNode*> st;
        TreeNode* pre = nullptr;
        st.push(root);

        while (!st.empty()) {
            TreeNode* cur = st.top(); st.pop();

            if (pre) {
                pre->left = nullptr;
                pre->right = cur;
            }
            if (cur->right) st.push(cur->right);
            if (cur->left) st.push(cur->left);
            
            pre = cur;
        }
    }
};
```

**启发：**

+ 遍历顺序可以根据不同的数据结构调整实现同样的效果。先序遍历下，队列是先push左结点，栈是先push右结点。
+ 最后一个结点的右指针一定是nullptr，所以不用处理。因此考虑用一个pre结点储存上一个结点的信息，进行遍历的处理操作。

#### 题解：（无敌代码）（直接构建）
```cpp
class Solution {
public:
    void flatten(TreeNode* root) {
        if (!root) return;
        
        // 递归展开左右子树
        flatten(root->left);
        flatten(root->right);
        
        // 保存右子树
        TreeNode* right = root->right;
        
        // 将左子树移到右子树位置
        root->right = root->left;
        root->left = nullptr;
        
        // 找到新右子树的最末端
        TreeNode* p = root;
        while (p->right) {
            p = p->right;
        }
        
        // 将原右子树接到最末端
        p->right = right;
    }
};
```

**启发：**

+ 把问题拆成基态。普遍情况。
+ 假设一棵树只有三层。 
    1. 先进入根结点的左子树，保存右节点，将左子树的左节点接到右节点上，再将右结点接到原左结点的右节点上；
    2. 保存根结点的右结点，然后将根结点的左结点接到右结点上…
    3. 循环操作。递归结束。
+ 递归方法是先按顺序递归到最后一层，再一层一层回去。先得进入函数，再依次退出。从底往上回退着走。



### 8.13 从前序与中序遍历序列构造二叉树
#### 题目：
给定两个整数数组 `preorder` 和 `inorder` ，其中 `preorder` 是二叉树的**先序遍历**， `inorder` 是同一棵树的**中序遍历**，请构造二叉树并返回其根节点。

**示例 1:**

![image-20260830154344635](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154344635.png)

```plain
输入: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
输出: [3,9,20,null,null,15,7]
```

**示例 2:**

```plain
输入: preorder = [-1], inorder = [-1]
输出: [-1]
```

**提示:**

+ `1 <= preorder.length <= 3000`
+ `inorder.length == preorder.length`
+ `3000 <= preorder[i], inorder[i] <= 3000`
+ `preorder` 和 `inorder` 均 **无重复** 元素
+ `inorder` 均出现在 `preorder`
+ `preorder` **保证** 为二叉树的前序遍历序列
+ `inorder` **保证** 为二叉树的中序遍历序列

#### 题解：（框范围）
```cpp
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    unordered_map<int, int> mp; // 记录中序遍历每个值对应的索引

    TreeNode* build(vector<int>& preorder, int preStart, int preEnd,
                    vector<int>& inorder, int inStart, int inEnd) {
        if (preStart > preEnd || inStart > inEnd) return nullptr;

        // 根节点的值
        int rootVal = preorder[preStart];
        TreeNode* root = new TreeNode(rootVal);

        // 根节点在中序遍历中的位置
        int pos = mp[rootVal];
        int leftSize = pos - inStart; // 左子树节点个数

        // 递归构建左子树
        root->left = build(preorder, preStart + 1, preStart + leftSize,
                           inorder, inStart, pos - 1);

        // 递归构建右子树
        root->right = build(preorder, preStart + leftSize + 1, preEnd,
                            inorder, pos + 1, inEnd);

        return root;
    }

    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        if (preorder.empty() || inorder.empty()) return nullptr;
        for (int i = 0; i < inorder.size(); ++i) mp[inorder[i]] = i;
        return build(preorder, 0, preorder.size() - 1,
                     inorder, 0, inorder.size() - 1);
    }
};
```

**启发：**

+ 先模拟手动构建原树的过程，再提炼过程转换为代码语言
+ 递归并不总是没有返回值。 
    - 在递归过程中处理返回值（全局变量）
    - 在递归结束后返回返回值，递归过程中处理、链接返回值。（构建子树根结点进行链接）
+ 根结点在中序遍历中从中间断开，找左右子树结点的范围比较容易。递归状态为范围
+ 用map来映射坐标，值对应的坐标



### 8.14 路径总和 III
#### 题目：
给定一个二叉树的根节点 `root` ，和一个整数 `targetSum` ，求该二叉树里节点值之和等于 `targetSum` 的 **路径** 的数目。

**路径** 不需要从根节点开始，也不需要在叶子节点结束，但是路径方向必须是向下的（只能从父节点到子节点）。

**示例 1：**

![image-20260830154353960](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154353960.png)

```plain
输入：root = [10,5,-3,3,2,null,11,3,-2,null,1], targetSum = 8
输出：3
解释：和等于 8 的路径有 3 条，如图所示。
```

**示例 2：**

```plain
输入：root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
输出：3
```

**提示:**

+ 二叉树的节点个数的范围是 `[0,1000]`
+ `$-10^9$ <= Node.val <= $10^9$`
+ `-1000 <= targetSum <= 1000`

**题解：（深度遍历）**

```cpp
**/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:

    int rootSum(TreeNode* root, long long targetSum) {
        if (!root) return 0;
        int ret = 0;
        if (root->val == targetSum) ret++;

        ret += rootSum(root->left, targetSum-root->val);
        ret += rootSum(root->right, targetSum-root->val);
        return ret;
    }

    int pathSum(TreeNode* root, int targetSum) {
        if (!root) return 0;

        int ans = rootSum(root, targetSum);
        ans += pathSum(root->left, targetSum);
        ans += pathSum(root->right, targetSum);
        return ans;
    }
};**
```

**灵感：**

+ 求和不一定是加法，也可以是知道和之后，算减法。
+ 方向只能是纵向，很容易联想到深度遍历，dfs
+ 所有路径，很容易联想到递归。起点结点可以为根、左孩子、右孩子，进行递归嵌套遍历所有路径。
+ 遍历函数中，通过减法判断值是否为0进行筛选路径。
+ 递归函数返回满足要求的路径数，主程序使用加法依次收集，最终返回。

**题解：（前缀和）**

```cpp
class Solution {
public:
    unordered_map<long long, int> prefix;

    int dfs(TreeNode *root, long long curr, int targetSum) {
        if (!root) {
            return 0;
        }

        int ret = 0;
        curr += root->val;
        if (prefix.count(curr - targetSum)) {
            ret = prefix[curr - targetSum];
        }

        prefix[curr]++;
        ret += dfs(root->left, curr, targetSum);
        ret += dfs(root->right, curr, targetSum);
        prefix[curr]--;

        return ret;
    }

    int pathSum(TreeNode* root, int targetSum) {
        prefix[0] = 1;
        return dfs(root, 0, targetSum);
    }
};
```





















#### 




## 09. 图论


## 10. 回溯


### 10.8 N 皇后
[51. N 皇后 - 力扣（LeetCode）](https://leetcode.cn/problems/n-queens/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:

    vector<vector<string>> solveNQueens(int n) {
        vector<vector<string>>ans;
        vector<bool> row(n, false);   
        vector<bool> col(n, false);   
        vector<bool> diag1(2*n-1, false); 
        vector<bool> diag2(2*n-1, false); 

        vector<string> board(n, string(n, '.'));

        auto dfs = [&] (auto&& self, int i) {

            if (i==n) {
                ans.emplace_back(board);
                return;
            }

            for (int j=0; j<n; ++j) {
                int d1 = i - j + n - 1;
                int d2 = i + j;

                if (row[i] || col[j] || diag1[d1] || diag2[d2]) continue;

                board[i][j] = 'Q';
                row[i] = col[j] = diag1[d1] = diag2[d2] = true;

                self(self, i + 1);

                board[i][j] = '.';
                row[i] = col[j] = diag1[d1] = diag2[d2] = false;
            }
        };

        dfs(dfs, 0);
        return ans;
    }
};
```

```cpp
class Solution {
public:
    vector<vector<string>> solveNQueens(int n) {
        auto solutions = vector<vector<string>>();
        auto queens = vector<int>(n, -1);
        solve(solutions, queens, n, 0, 0, 0, 0);
        return solutions;
    }

    void solve(vector<vector<string>> &solutions, vector<int> &queens, int n, int row, int columns, int diagonals1, int diagonals2) {
        if (row == n) {
            auto board = generateBoard(queens, n);
            solutions.push_back(board);
        } else {
            int availablePositions = ((1 << n) - 1) & (~(columns | diagonals1 | diagonals2));
            while (availablePositions != 0) {
                int position = availablePositions & (-availablePositions);
                availablePositions = availablePositions & (availablePositions - 1);
                int column = __builtin_ctz(position);
                queens[row] = column;
                solve(solutions, queens, n, row + 1, columns | position, (diagonals1 | position) >> 1, (diagonals2 | position) << 1);
                queens[row] = -1;
            }
        }
    }

    vector<string> generateBoard(vector<int> &queens, int n) {
        auto board = vector<string>();
        for (int i = 0; i < n; i++) {
            string row = string(n, '.');
            row[queens[i]] = 'Q';
            board.push_back(row);
        }
        return board;
    }
};

```

:::tips
反思：

+ 到底是数组的下标，还是数组下标对应的值，要搞清楚
+ 给 string 初始化值，vector<string> board(n, string(n, '.'))
+ string(n, '.') ：创建一个长度为 n 并且所有字符都是 'n' 的字符串

:::



## 11. 二分查找


## 12. 栈


## 13. 堆


## 14. 贪心算法


### 14.1 买卖股票的最佳时机


[121. 买卖股票的最佳时机 - 力扣（LeetCode）](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/description/?envType=study-plan-v2&envId=top-100-liked)



```cpp
// 思路：
// 从前往后获取每个下标的最小值
// 从后往前获取每个下标的最大值
// 遍历数组，计算每个下标的最大值与最小值的差
// 遍历数组，获取差值的最大值，即为最终的答案
// 时间复杂度: O(n)，一共需要遍历 4 次数组
// 空间复杂度: O(n)，需要两个数组的空间，其余均为单一变量

class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int size = prices.size();

        if (size <= 1) return 0;
        if (size == 2) return 0 > prices[1]-prices[0] ? 0 : prices[1] - prices[0];

        vector<int> v_min(size);
        vector<int> v_max(size);

        v_min[0] = prices[0];
        v_max[size-1] = prices[size-1];

        for (int i=1; i<size; ++i) {
            if (prices[i] < v_min[i-1]) {
                v_min[i] = prices[i];
            } else {
                v_min[i] = v_min[i-1];
            }
        }

        for (int j=size-2; j>0; --j) {
            if (prices[j] > v_max[size-1]) {
                v_max[j] = prices[j];
            } else {
                v_max[j] = v_max[j+1];
            }
        }

        int ans = 0;
        for (int i=0; i<size; ++i) {
            ans = max(ans, v_max[i] - v_min[i]);
        }
        return ans;
    }
};
```

```cpp
// 假设是在今天 i 卖股票，那么买入时机一定是 [0,i-1] 天内的最小值买入
// 巧妙在固定了卖出的时间，利用了买入时间一定小于卖出时间的特性
// 注：其实我也考虑过这个特性，但是利用得不够好，或者说遍历顺序不够好。我利用首尾双指针同时移动
// 	   导致顺序上有漏洞
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int inf = 1e9;
        int minprice = inf, maxprofit = 0;
        for (int price: prices) {
            maxprofit = max(maxprofit, price - minprice);
            minprice = min(price, minprice);
        }
        return maxprofit;
    }
};
```



### 14.2 跳跃游戏


[55. 跳跃游戏 - 力扣（LeetCode）](https://leetcode.cn/problems/jump-game/?envType=study-plan-v2&envId=top-100-liked)



```cpp
// 思路：
// 		遍历从当前开始，可以到达的所有位置，打上可以到达的标记
// 		然后，到下一个位置再更新能到达的所有位置
// 		最后，判断终点能否到达
// 一个标记数组，遍历一次数组

class Solution {
public:
    bool canJump(vector<int>& nums) {
        int size = nums.size();
        vector<int> visitable(size);
        visitable[0] = 1;
        for (int i=0; i<size; ++i) {
            if (visitable[i] == 1) {
                for (int j=1; j<=nums[i]; ++j) {
                    if (i+j < size) visitable[i+j] = 1;
                }
            }
        }
        if (visitable[size-1] == 1) return true;
        return false;
    }
};
```

```cpp
// 100% 93%
// 优化思路：
// 		仍然需要遍历一次数组，不用标记数组，用一个常量记录能跳跃的最远位置
// 		在小于最远距离内，继续遍历，直到最远位置处，，是否还有跳得更远的，更新能到达的最远位置
// 		结束判断，最远位置是否为终点
// 一次遍历，O(1)常量空间
class Solution {
public:
    bool canJump(vector<int>& nums) {
        int size = nums.size();
        int fp = nums[0];

        for (int i=0; i<=fp && i < size; ++i) {
            if (i+nums[i]>fp) fp=i+nums[i];
        }
        if (fp >= size-1) return true;
        return false;
    }
};
```



### 14.3 跳跃游戏 Ⅱ


[45. 跳跃游戏 II - 力扣（LeetCode）](https://leetcode.cn/problems/jump-game-ii/description/?envType=study-plan-v2&envId=top-100-liked)



```cpp
// 我的思路：计算到达所有位置所需的最小跳跃次数
class Solution {
public:
    int jump(vector<int>& nums) {
        int size = nums.size();
        vector<int> dp(size);
        for (int i=0; i<size; ++i) {
            dp[i] = 1e4;
        }
        dp[0] = 0;
        for (int i=0; i<size; ++i) {
            for (int j=nums[i]; j>0; --j) {
                if (i+j < size) {
                    dp[i+j] = min(dp[i]+1, dp[i+j]);
                }
            }
        }
        return dp[size-1];
    }
};
```

```cpp
// 思路：下一次跳跃可到达的位置中，从哪一个位置出发能到达更远的距离
// 		确定从“可选的出发位置”中出发能到达最远位置的出发位置
// 核心：遍历从当前位置到跳跃的最远位置处，核心在最远位置，这是边界，
// 		遍历完后，得到一个下次遍历的边界，贪心这个最远边界
class Solution {
public:
    int jump(vector<int>& nums) {
        int n = nums.size();
        if (n <= 1) return 0;
        
        int jumps = 0;
        int current_end = 0;
        int next_end = 0;
        
        for (int i = 0; i < n - 1; ++i) {
            next_end = max(next_end, i + nums[i]);
            
            if (i == current_end) {
                jumps++;
                current_end = next_end;
                if (current_end >= n - 1) {
                    break; // 提前终止，已覆盖末尾
                }
            }
        }
        return jumps;
    }
};
```





### 经验总结


贪心的思考纬度：

+ 先固定一个值，贪心剩下的
+ 倒着推，先贪心结果，看过程是否满足
+ 想清楚贪心的目标是什么，是否通过贪心这个**目标**一定能得到最优解（转化求解目标，映射关系）











## 15. 动态规划


### 15.9 分割等和子集
[416. 分割等和子集 - 力扣（LeetCode）](https://leetcode.cn/problems/partition-equal-subset-sum/description/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int total = 0;
        for (int num : nums) total += num;
        if (total % 2 != 0) return false;
        
        int target = total / 2;
        // dp[j] 表示能否凑出和为j的子集
        vector<bool> dp(target + 1, false);
        dp[0] = true; // 初始状态：和为0可以凑出
        
        for (int num : nums) {
            // 逆序遍历，避免重复使用同一元素
            for (int j = target; j >= num; --j) {
                dp[j] = dp[j] || dp[j - num];
            }
        }
        
        return dp[target];
    }
};
```

```cpp
// 简化了内容的版本。本来按照思路是 dp[i][j] 的
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int n = nums.size();
        if (n < 2) {
            return false;
        }
        int sum = 0, maxNum = 0;
        for (auto& num : nums) {
            sum += num;
            maxNum = max(maxNum, num);
        }
        if (sum & 1) {
            return false;
        }
        int target = sum / 2;
        if (maxNum > target) {
            return false;
        }
        vector<int> dp(target + 1, 0);
        dp[0] = true;
        for (int i = 0; i < n; i++) {
            int num = nums[i];
            for (int j = target; j >= num; --j) {
                dp[j] |= dp[j - num];
            }
        }
        return dp[target];
    }
};
```

```cpp
// 核心思想是：选或不选该数
class Solution {
public:	
  //暴力解法：要判断是否为奇偶，是个好的剪纸
    bool canPartition(vector<int>& nums) {
      sort(nums.begin(), nums.end());
      int sum = accumulate(nums.begin(), nums.end(), 0);
      if (sum & 1) return false;
      return can(nums, nums.size() - 1, 0, sum);
    }
    bool can(vector<int>& nums, int pos, int now, int sum) {
      if (now * 2 == sum) return true;
      if (now * 2 > sum) return false;
      if (pos < 0) return false;
      if ((now + nums[pos] * 2) > sum) return false;//这是最大的剪枝，但不知道为啥是对的，常用的去重枚举也是可以的
      return can(nums, pos - 1, now + nums[pos], sum) || can(nums, pos - 1, now, sum);
    }
  //0-1背包  记忆化搜索等 都可以做
    // bool canPartition(vector<int>& nums) {
    //   //solution1
    //   int sum = accumulate(nums.begin(), nums.end(), 0);
    //   vector<vector<int>> dp(nums.size() + 1, vector<int>(sum/2 + 1, 0));
    //   for (int i = 1; i <= nums.size(); ++ i) {
    //     for (int j = nums[i-1]; j <= sum/2; ++ j) {
    //       dp[i][j] = max(dp[i-1][j], dp[i-1][j - nums[i-1]] + nums[i-1]);
    //     }
    //   }
    //   return dp[nums.size()][sum/2] * 2 == sum;
    // }
};
```

## 16. 多维动态规划


### 16.1 不同路径
[62. 不同路径 - 力扣（LeetCode）](https://leetcode.cn/problems/unique-paths/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:
    int uniquePaths(int m, int n) {
        vector<vector<int>> mp(m+1, vector<int>(n+1));
        for (int i=1; i<=m; ++i) mp[i][1]=1;
        for (int i=1; i<=n; ++i) mp[1][i]=1;

        for (int i=2; i<=m; ++i) {
            for (int j=2; j<=n; ++j) {
                mp[i][j]=mp[i][j-1]+mp[i-1][j];
            }
        }
        return mp[m][n];
    }
};
```

```cpp
class Solution {
public:
    int uniquePaths(int m, int n) {
        long long ans = 1;
        for (int x = n, y = 1; y < m; ++x, ++y) {
            // 省略 1w 步复杂的公式推理
            ans = ans * x / y;
        }
        return ans;
    }
};
```



### 16.2 最小路径和
[64. 最小路径和 - 力扣（LeetCode）](https://leetcode.cn/problems/minimum-path-sum/description/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:
    int minPathSum(vector<vector<int>>& grid) {
        int m=grid.size(), n=grid[0].size();
        vector<vector<int>> mp(m, vector<int>(n, 0));
        mp[0][0]=grid[0][0];
        for (int i=1; i<m; ++i) mp[i][0]=grid[i][0]+mp[i-1][0];
        for (int i=1; i<n; ++i) mp[0][i]=grid[0][i]+mp[0][i-1];

        for (int i=1; i<m; ++i) {
            for (int j=1; j<n; ++j) {
                mp[i][j]=min(mp[i-1][j], mp[i][j-1])+grid[i][j];
            }
        }

        return mp[m-1][n-1];
    }
};
```

```cpp

```



### 16.3 最长回文子串
[5. 最长回文子串 - 力扣（LeetCode）](https://leetcode.cn/problems/longest-palindromic-substring/description/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:
    string longestPalindrome(string s) {
        int n = s.size();
        if (n == 0) return "";
        int ansIdx = 0;
        int ansLen = 1; // 初始化为1，处理单字符情况
        // s 由数字和英文字母组成，ASCII 编码下都是 int 类型
        unordered_map<char, vector<int>> mp; // 键改为char，更直观

        // 记录每个字符的下标集合
        for (int i = 0; i < n; ++i) {
            mp[s[i]].push_back(i);
        }

        // 遍历每个字符的下标集合
        for (const auto& pair : mp) {
            const vector<int>& arr = pair.second;
            int m = arr.size();
            // 从前往后遍历左端点
            for (int i = 0; i < m; ++i) {
                int left = arr[i];
                if (n - left <= ansLen) break;  // 剪枝：剩余最大可能长度 <= 当前最长，直接break
                // 从后往前遍历右端点
                for (int j = m - 1; j > i; --j) {
                    int right = arr[j];
                    int curLen = right - left + 1;
                    if (curLen <= ansLen) break;  // 剪枝：当前长度 <= 当前最长，break（j递减，curLen越来越小）
                    // 首尾双指针判断是否为回文
                    int l = left, r = right;
                    bool isPalindrome = true;
                    while (l < r) {
                        if (s[l] != s[r]) {
                            isPalindrome = false;
                            break;
                        }
                        ++l; --r;
                    }
                    // 判断为回文子串
                    if (isPalindrome) {
                        ansIdx = left;
                        ansLen = curLen;
                        break; // 剪枝：找到当前i对应的最长回文，直接break
                    }
                }
            }
        }
        return s.substr(ansIdx, ansLen);
    }
};
```

```cpp
// dp 标记状态，临界点判断，从小到大遍历回文串的长度的可能长度
class Solution {
public:
    string longestPalindrome(string s) {
        int n = s.size();
        if (n < 2) {
            return s;
        }

        int maxLen = 1;
        int begin = 0;
        // dp[i][j] 表示 s[i..j] 是否是回文串
        vector<vector<int>> dp(n, vector<int>(n));
        // 初始化：所有长度为 1 的子串都是回文串
        for (int i = 0; i < n; i++) {
            dp[i][i] = true;
        }
        // 递推开始
        // 先枚举子串长度
        for (int L = 2; L <= n; L++) {
            // 枚举左边界，左边界的上限设置可以宽松一些
            for (int i = 0; i < n; i++) {
                // 由 L 和 i 可以确定右边界，即 j - i + 1 = L 得
                int j = L + i - 1;
                // 如果右边界越界，就可以退出当前循环
                if (j >= n) {
                    break;
                }

                if (s[i] != s[j]) {
                    dp[i][j] = false;
                } else {
                    if (j - i < 3) {
                        dp[i][j] = true;
                    } else {
                        dp[i][j] = dp[i + 1][j - 1];
                    }
                }

                // 只要 dp[i][L] == true 成立，就表示子串 s[i..L] 是回文，此时记录回文长度和起始位置
                if (dp[i][j] && j - i + 1 > maxLen) {
                    maxLen = j - i + 1;
                    begin = i;
                }
            }
        }
        return s.substr(begin, maxLen);
    }
};
```

```cpp
// 有想过这种思路，只是怎么找中心没想出来
//枚举所有的「回文中心」并尝试「扩展」，贪心到无法再扩展截止
class Solution {
public:
    pair<int, int> expandAroundCenter(const string& s, int left, int right) {
        while (left >= 0 && right < s.size() && s[left] == s[right]) {
            --left;
            ++right;
        }
        return {left + 1, right - 1};
    }

    string longestPalindrome(string s) {
        int start = 0, end = 0;
        for (int i = 0; i < s.size(); ++i) {
            auto [left1, right1] = expandAroundCenter(s, i, i); // 回文中心是一个字符
            auto [left2, right2] = expandAroundCenter(s, i, i + 1); // 回文中心是两个字符
            if (right1 - left1 > end - start) {
                start = left1;
                end = right1;
            }
            if (right2 - left2 > end - start) {
                start = left2;
                end = right2;
            }
        }
        return s.substr(start, end - start + 1);
    }
};
```



### 16.4 
[1143. 最长公共子序列 - 力扣（LeetCode）](https://leetcode.cn/problems/longest-common-subsequence/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:
    int longestCommonSubsequence(string text1, string text2) {
        int size1 = text1.size();
        int size2 = text2.size();

        vector<vector<int>> dp(size1+1, vector<int>(size2+1, 0));

        for (int i=1; i<=size1; ++i) {
            for (int j=1; j<=size2; ++j) {
                if (text1[i-1]==text2[j-1]) dp[i][j] = dp[i-1][j-1]+1;
                else dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
            }
        }

        return dp[size1][size2];
    }
};
```



### 16.5
[72. 编辑距离 - 力扣（LeetCode）](https://leetcode.cn/problems/edit-distance/?envType=study-plan-v2&envId=top-100-liked)

```cpp
class Solution {
public:
    int minDistance(string word1, string word2) {
        int len1 = word1.size();
        int len2 = word2.size();
        if (len1 * len2 == 0) return len1 + len2;
        vector<vector<int>> dp(len1+1, vector<int>(len2+1, 0));

        for (int i=0; i<=len1; ++i) dp[i][0]=i;
        for (int j=0; j<=len2; ++j) dp[0][j]=j;

        for (int i=1; i<=len1; ++i) {
            for (int j=1; j<=len2; ++j) {
                if (word1[i-1]==word2[j-1]) dp[i][j] = min(dp[i-1][j]+1, min(dp[i][j-1]+1, dp[i-1][j-1]));
                else dp[i][j] = 1 + min(dp[i-1][j], min(dp[i][j-1], dp[i-1][j-1]));
            }
        }
        return dp[len1][len2];
    }
};
```

:::tips
总结：

+ 一类典型的范围 dp 的题。规划的特征不是一一对应的状态，而是范围内的规划，范围内的最小值
+ 做题套路：
    - 规划对象不是第 (i, j) 个状态，而是前 i 个和前 j 个状态的**最佳**状态
    - 状态转移还是得一步一步地进行转移，上一个操作到下一个操作的所有情况数。  
    dp[i][j] -> dp[i-1][j] | dp[i][j-1] | dp[i-1][j-1] 通常是这 3 种状态
    - 初始状态进行初始化值
+ 该题有个巧代码：if (len1 * len2 == 0) return len1 + len2;   
		--> 当 len1==0 | len2==0 时，返回非零值

:::



## 17. 技巧














# 题型技巧


## 链表


在 C++ 算法竞赛中，链表题的核心特点是**指针操作密集、边界条件多、代码容错率低**，但题型套路性强，掌握通用思路和技巧后可高效破解。以下从「通用分析思路、题型分类及特点、核心技巧、常见坑点、优化方向、经典例题映射」六个维度，系统解析链表题的解法框架：

### <font style="color:rgb(0, 0, 0);">一、通用分析思路（拿到链表题的 5 步流程）</font>
链表题的难点在于「指针绕晕」和「边界遗漏」，按以下流程拆解可快速破题：

#### <font style="color:rgb(0, 0, 0);">1. 审题定类型</font>
+ 明确链表结构：**单链表（最常见）、双链表（LRU / 模拟题）、循环链表（环相关题）**；
+ 明确问题目标：是「反转、合并、删除、查找、重构」中的哪一类；
+ 明确限制条件：是否要求「原地操作（O (1) 空间）」、「一次遍历（O (n) 时间）」。

#### <font style="color:rgb(0, 0, 0);">2. 画图建模</font>
**链表题必画图！** 用简单符号标记节点（如 `A→B→C→D`），标注关键操作（如反转时的`prev/curr/next`、删除时的`prev/curr`），避免指针操作断链。

#### <font style="color:rgb(0, 0, 0);">3. 选择核心方法</font>
根据题型匹配技巧（如反转用「三指针」，找环用「快慢指针」，合并用「双指针」），优先选择「时间最优 + 空间最优」的方案（竞赛中常要求 O (n) 时间、O (1) 空间）。

#### <font style="color:rgb(0, 0, 0);">4. 先处理边界</font>
链表题的边界错误占比超 60%，优先写「特殊情况」的判定：

+ 空链表（`head == nullptr`）；
+ 单节点链表（`head->next == nullptr`）；
+ 双节点链表（`head->next->next == nullptr`）；
+ 操作涉及首尾节点（如删除头节点、反转尾节点）。

#### <font style="color:rgb(0, 0, 0);">5. 分步实现 + 验证</font>
复杂操作拆分成小步骤（如「k 个一组反转」拆分为「分组→反转每组→连接各组」），每一步修改指针后，在脑中 / 纸上验证链表是否连续，避免断链。

### <font style="color:rgb(0, 0, 0);">二、题型分类及核心特点</font>
链表题在竞赛中题型高度固定，以下是高频题型及核心特征：

| **题型** | **核心特征** | **经典例题（LeetCode 对应）** |
| :--- | :--- | :--- |
| 反转类（整体 / 部分） | 指针回溯，需保存前驱 / 后继节点，避免断链 | 206. 反转链表、92. 反转链表 II、25.k 个一组反转 |
| 合并 / 拆分类 | 双指针遍历，按条件合并 / 拆分，需处理长短差异 | 21. 合并两个有序链表、86. 分隔链表 |
| 删除类 | 找目标节点的前驱，或用快慢指针定位，需判空 | 19. 删除倒数第 k 个节点、83. 删除重复节点 |
| 查找类 | 环 / 交点 / 中间节点，依赖双指针（快慢 / 同步） | 141. 环形链表、142. 环形链表 II、160. 相交链表 |
| 重构类 | 拆分 + 反转 + 合并，多步骤组合 | 143. 重排链表、24. 两两交换节点 |
| 双链表 / 循环链表操作 | 前后指针双向操作，插入 / 删除 O (1)，需处理环 | 146.LRU 缓存（双链表 + 哈希）、设计循环双端队列 |


#### <font style="color:rgb(0, 0, 0);">各题型核心逻辑</font>
1. **反转类**：核心是「三指针法」（`prev=nullptr, curr=head, next=curr->next`），本质是「逐个节点修改指向」。
    - 整体反转：循环修改`curr->next=prev`，再依次移动三指针；
    - 部分反转（如反转从 left 到 right 的节点）：先找到 left 的前驱，再对 [left, right] 区间执行三指针反转，最后连接前后段；
    - k 个一组反转：先遍历统计长度，再分组反转，每组反转后连接前驱组和后继组。
2. **合并 / 拆分类**：
    - 合并有序链表：双指针`p1/p2`分别指向两个链表，比较`p1->val`和`p2->val`，小的接入结果链表；
    - 拆分链表（如奇偶拆分）：双指针`odd/even`分别指向奇偶节点，遍历后连接奇数尾和偶数头。
3. **删除类**：
    - 删除指定值：用`prev`跟踪前驱，`curr`遍历，找到目标节点后`prev->next=curr->next`；
    - 删除倒数第 k 个：快慢指针（快指针先走 k 步，再同步走，快指针到尾时慢指针指向目标前驱）。
4. **查找类**：
    - 找环：快慢指针（快指针每次 2 步，慢指针每次 1 步，相遇则有环）；
    - 找环入口：相遇后将快指针重置为 head，两指针同步走，再次相遇即为入口；
    - 找中间节点：快慢指针（快指针到尾时，慢指针在中间）；
    - 找相交链表：双指针同步遍历，A 遍历完转 B，B 遍历完转 A，相遇则为交点（抵消长度差）。
5. **重构类**：如重排链表（`L0→L1→…→Ln-1→Ln` → `L0→Ln→L1→Ln-1→…`）：拆分为「找中间节点→反转后半段→合并前后两段」三步。

### <font style="color:rgb(0, 0, 0);">三、核心技巧（必掌握，竞赛提分关键）</font>
#### <font style="color:rgb(0, 0, 0);">1. 哑节点（Dummy Node）—— 解决头节点麻烦</font>
**作用**：避免单独处理「头节点被修改 / 删除」的情况（如删除头节点、反转后头节点变化），统一链表操作逻辑。**用法**：定义`ListNode* dummy = new ListNode(0); dummy->next = head;`，后续操作围绕`dummy->next`展开，最后返回`dummy->next`。

**示例**：删除倒数第 k 个节点（LeetCode 19）如果直接操作 head，当 k 等于链表长度时，删除的是头节点，需单独处理；用 dummy 后，快慢指针从 dummy 开始，无需特殊判断。

#### <font style="color:rgb(0, 0, 0);">2. 三指针法 —— 反转类题的万能模板</font>
**核心逻辑**：用`prev`（前驱）、`curr`（当前）、`next`（后继）三个指针，避免修改`curr->next`后丢失后续节点。**模板代码**（整体反转）：

**cpp**

运行

```cpp
ListNode* reverseList(ListNode* head) {
    ListNode *prev = nullptr, *curr = head;
    while (curr != nullptr) {
        ListNode* next = curr->next; // 先保存后继
        curr->next = prev;           // 反转当前节点指向
        prev = curr;                 // 移动前驱
        curr = next;                 // 移动当前
    }
    return prev; // prev成为新头
}
```

#### <font style="color:rgb(0, 0, 0);">3. 双指针法 —— 查找 / 合并 / 删除的高效工具</font>
双指针分为「快慢指针」和「同步指针」，核心是「利用指针速度差 / 同步遍历」优化时间复杂度：

+ **快慢指针**：解决「环、中间节点、倒数 k 个节点」（O (n) 时间，O (1) 空间）；
+ **同步指针**：解决「合并有序链表、相交链表」（O (n+m) 时间，O (1) 空间）。

#### <font style="color:rgb(0, 0, 0);">4. 原地操作 —— 空间优化的关键</font>
竞赛中链表题常要求「O (1) 空间复杂度」，禁止用数组 / 栈存储节点，需通过指针操作直接修改原链表：

+ 反例：用栈存储节点再弹出实现反转（O (n) 空间，不推荐）；
+ 正例：三指针反转（O (1) 空间）。

#### <font style="color:rgb(0, 0, 0);">5. 双链表技巧 —— 应对 LRU / 模拟题</font>
双链表的`prev`和`next`指针支持「前驱 / 后继节点的 O (1) 访问」，核心操作：

+ 插入节点：`node->prev = prev; node->next = next; prev->next = node; next->prev = node;`；
+ 删除节点：`prev->next = node->next; node->next->prev = prev;`；
+ 注意：循环双链表需处理「首尾节点的 prev/next 指向」（如尾节点的 next 指向头节点）。

#### <font style="color:rgb(0, 0, 0);">6. 哈希表辅助 —— 空间换时间（必要时用）</font>
当需要「快速查找节点地址」时（如判断环、找相交节点、LRU 缓存），用哈希表`unordered_map<ListNode*, bool>`存储节点是否访问过，或`unordered_map<int, ListNode*>`存储键值对应节点（LRU）。**注意**：仅当 O (n) 空间被允许时使用，优先用双指针优化。

### <font style="color:rgb(0, 0, 0);">四、常见坑点（避坑 = 提分）</font>
链表题的错误 80% 集中在以下几点，必须重点规避：

#### <font style="color:rgb(0, 0, 0);">1. 空指针访问（最致命）</font>
+ 错误：`curr->next->val` 未判断`curr->next是否为null`；
+ 规避：所有指针访问前先判空（如`if (curr == nullptr || curr->next == nullptr) break;`）。

#### <font style="color:rgb(0, 0, 0);">2. 指针修改顺序错误（断链）</font>
+ 错误：反转时先`curr->next = prev`，再`next = curr->next`（此时`next`已变成`prev`，丢失后续节点）；
+ 规避：**先保存后继节点，再修改当前节点指向**（三指针法的核心顺序）。

#### <font style="color:rgb(0, 0, 0);">3. 边界条件遗漏</font>
+ 错误：只考虑一般情况，忽略「空链表、单节点、删除头节点、反转尾节点」；
+ 规避：写代码前先列 3-5 个测试用例（空、单节点、双节点、一般情况、边界情况），先处理特殊用例。

#### <font style="color:rgb(0, 0, 0);">4. 循环条件错误</font>
+ 错误：`while (curr->next != nullptr)` 和 `while (curr != nullptr)` 混淆（前者遍历到倒数第二个节点，后者遍历到尾节点）；
+ 规避：根据需求选择循环条件（如反转需遍历到尾节点，用`curr != nullptr`；删除节点需找前驱，用`curr->next != nullptr`）。

#### <font style="color:rgb(0, 0, 0);">5. 混淆「节点值」和「节点地址」</font>
+ 错误：判断相交链表时，比较`p1->val == p2->val`（值可能相同但地址不同，不是真交点）；
+ 规避：链表相交 / 环的判断，比较「节点指针地址」（`p1 == p2`）。

### <font style="color:rgb(0, 0, 0);">五、优化方向（竞赛追求极致效率）</font>
1. **时间优化**：
    - 避免多次遍历：如找中间节点用快慢指针（1 次遍历），而非先统计长度再遍历一半（2 次遍历）；
    - 批量处理：如 k 个一组反转，分组后批量反转，减少指针操作次数。
2. **空间优化**：
    - 坚决不用额外空间存储节点（如数组、栈），优先原地操作；
    - 哈希表仅在必要时使用（如 LRU 缓存，无替代方案）。
3. **代码简洁性优化**：
    - 提取重复操作成函数：如「反转一段链表」可写成独立函数`ListNode* reverse(ListNode* start, ListNode* end)`，供多题复用；
    - 用哑节点减少条件判断：统一头节点和非头节点的操作逻辑。

### <font style="color:rgb(0, 0, 0);">六、总结（核心口诀 + 练习建议）</font>
#### <font style="color:rgb(0, 0, 0);">核心口诀</font>
+ 链表题，先画图；边界 case 先处理；
+ 反转用三指针，查找用双指针；
+ 头节点麻烦用 dummy，断链风险先存 next；
+ 环和交点比地址，原地操作是关键。

#### <font style="color:rgb(0, 0, 0);">练习建议</font>
1. 按题型刷题：先刷「反转→合并→删除→查找→重构→双链表」，每个题型刷 2-3 题，掌握模板；
2. 经典题必刷：LeetCode 206、92、25、21、19、141、142、143、24、146（覆盖所有核心题型）；
3. 复盘错误：重点记录「空指针访问、边界遗漏、指针顺序错误」，形成避坑清单。



# 经验之谈


## 01- 实现 01 之间的数字切换类似开关


```cpp
int flag = 0;
if (true) flag^=1; // flag=1
if (true) flag^=1; // flag=0
```



## 02 - 一定要阅读提示的参数范围


![image-20260830154424843](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154424843.png)

有的时候参数范围是关键的简化信息。可以通过范围得出算法的复杂度大致区间，能不能用暴力来求解。



## 03 -  有理数的乘除**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">本质上就是对质因数的幂次做加减运算</font>**


[3850. 统计结果等于 K 的序列数目 - 力扣（LeetCode）](https://leetcode.cn/problems/count-sequences-to-k/description/?envType=problem-list-v2&envId=kpoiskru&)



1. 任何正有理数都能写成：

$ r=\frac{整数}{整数}=\frac{分子}{分母} $

2. 任何正整数都能唯一分解成质因数的幂次乘积（算数基本定理）：

$ n=p_1^{a_1} p_2^{a_2} \dots p_k^{a_k} $

即： 任何一个有理数，都可以唯一写成「若干个质数的整数次幂相乘」的形式。  



## 04 - 正推与倒推会有不同的效果


+ 当倒序遍历时，有时最终结果可能回归到 1 ，更方便理清思路，降低思考复杂度，利用 1 的特性

[3850. 统计结果等于 K 的序列数目 - 力扣（LeetCode）](https://leetcode.cn/problems/count-sequences-to-k/description/?envType=problem-list-v2&envId=kpoiskru&)

| 原操作（1→k） | 反向操作（k→1） | 幂次变化<br/>（nums [i] 的质因子为 x,y,z） |
| :---: | :---: | :---: |
| val × nums[i] | k ÷ nums[i] | e2-x、e3-y、e5-z（减幂次） |
| val ÷ nums[i] | k × nums[i] | e2+x、e3+y、e5+z（加幂次） |
| val 不变 | k 不变 | e2、e3、e5 不变 |




其实这道例题，正推倒推效果是一样的，原因如下：

+ 遍历效果相同：正推的起始与倒退的起始都是固定的。正推从 1 开始以 k 结尾，倒推以 k 开始以 1 结尾，
+ dfs 搜索方式相同：dfs 的搜索方式都是一样的，3 种情况都需要进行遍历搜索



![image-20260830154436792](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260830154436792.png)



## 05 - 当需要大量进行重复判断时，可以用缓存减少计算次数


空间换时间，大幅度减少计算时间，降低超时概率



## 06 - 简便的解包操作处理多返回值


使用 `auto [v1, v2, ..., vn] = ...` 的格式完成快速解包操作。



```cpp
tuple<long long, bool> primeFactorization(long long k) {};	
auto [e, ok] = primeFactorization(n);	
```

```cpp
map<int, string> mp = {};
for (auto [k, v]: mp) {};
```

```cpp
int arr[3] = {10, 20, 30};
auto [a, b, c] = arr;
cout << a << " " << b << " " << c << endl; // 输出：10 20 30
```



解包对象需要修改时，auto& 加上引用，否则为只读。



## 07 - 运用 lambda 表达式的灵活性


> 待补充学习
>



## 08 - 去除质因数


> 对一个数进行去除质因数操作，除以所有指定的质因数
>
> 只需要一直除以这个数，直到除不尽即可
>



```cpp
int e3 = 0; // 记录质因数 3 的个数
int num = 135; // 当前数
while (num % 3 == 0) {
    ++e3;
    num /= 3;
}

int func(int num, int e) {
    while (num % e == 0) num /= e;
    return num;
}
```



## 09 - 位运算分段编码


> 有的情况下，需要对状态进行缓存记录，减少重复计算次数，降低 timeout 的风险。
>
> 添加缓存的时候，需要对状态进行唯一编码进行哈希表存储。可以将状态进行位运算分段编码。
>



```cpp
int i,e2,e3,e5; // 一共 4 个状态
int key = i<<21 | (e2+n*2)<<14 | (e3+n)<<7 | (e5+n); // n 为一个常数，与题意相关
```

解释：

+ 先对数据进行非负处理，哈希表不支持负数索引。计算其最小值映射数据范围
+ 关注需要编码的数据的范围：（由题意可得）
    - i 的最大值为 19，二进制占 5 位
    - e2 为 0-75，二进制占 7 位
    - e3 为 0-38，二进制占 6 位（用 7 位没问题）
    - e5 为 0-38，二进制占 6 位（用 7 位没问题）
+ 一个 int 类型为 32 位，5 位、7 位、7 位、7 位加起来小于 32 位，够用，不会导致位冲突。如果不够用：
    - 可以考虑使用 uint64_t 类型
    - 直接将整个状态组合码作为索引，tuple<int,int,int,int>，利用 map 的红黑树结构进行查找值
    - map 可以嵌套，多个 map 相互嵌套，每个 map 只处理一个状态，保证够用。map[i][e2][e3][e5]
+ 位运算符：
    - <<：向左移位，箭头指向左
    - >>：向右移位，箭头指向右
    - |：按或运算，进行二进制数的拼接操作（这里的不同的二进制数使用的位数各不同，可以直接拼接）



| 位数 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 值 | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 |
| 范围 | [0,1] | [0,3] | [0,7] | [0,15] | [0,31] | [0,63] | [0,127] | [0,257] |




## 10 - pow() 函数的返回值是浮点数类型


## 11 - 注意值的数据范围 int 与 long long


## 12 - 一行代码求解容器的最值


> 底层实现：线性遍历 O(n) O(1)
>



```cpp
vector<int> arr({1, 2, 5, 234, 64, 24});
int mn = ranges::min(arr);
int mx = ranges::max(arr);
cout << mn << "  " << mx << endl;
```



## 13 - lambda 表达式的运用


> 通常用来调整作用域。
>
> 有时需要写一个函数来遍历所有可能情况，需要用到一些变量，但是这个函数是全局函数，不能访问到入口函数的形参，就需要用到全局变量。使用全局变量修改比较麻烦，就通过 lambda 表达式直接把这个遍历函数写到内部，使用形参变量。
>



语法格式：

```cpp
[捕获列表] (参数列表) -> 返回值类型 { 函数体 }
```

+ 捕获列表：必写，[] 表示不捕获外部值
    - 捕获值，只读。[变量名]，[=] 表示捕获所有值。
    - 捕获引用，可写。[&变量名]，[&] 表示捕获所有引用。
+ 参数列表：可选
+ 返回值类型：可选，会自动推导返回值类型



## 14 - 高效判断奇偶


```cpp
int target = 3242;
if (target & 1) cout << "奇数" << endl;
else cout << "偶数" << endl;
```







# 难题收录


[3850. 统计结果等于 K 的序列数目 - 力扣（LeetCode）](https://leetcode.cn/problems/count-sequences-to-k/description/)



考点：

+ 质因数分解函数
+ 有理数乘除的本质
+ 缓存机制 + 状态编码
+ dfs 递归搜索
+ 二进制操作



<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">核心解题思路（纯文字无细节版）</font>

1. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">数学简化：将有理数的乘除运算转化为质因子幂次的增减运算，同时快速判断是否存在无解的情况。</font>
2. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">问题逆向：将从初始值出发凑出目标值的正向问题，转化为从目标值出发凑出初始值的逆向问题，明确每个元素对应的操作方向。</font>
3. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">递归计算：通过递归的方式遍历所有可能的操作组合，统计符合条件的操作序列数量。</font>
4. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">缓存优化：缓存递归过程中重复出现的状态，避免重复计算以降低时间复杂度。</font>

<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);"></font>

```cpp
class Solution {
public:

    pair<tuple<int, int, int>, bool> primeFactorization(long long k) {
        // 返回质因数的幂组合，以及是否只含有 2， 3， 5 这 3 个质因数
        int e2 = countr_zero((uint64_t) k);
        k>>=e2;

        int e3 = 0;
        while (k%3 == 0) {
            ++e3;
            k/=3;
        }

        int e5=0;
        while(k%5==0) {
            ++e5;
            k/=5;
        }
        // 该数的因数中含有 e2 个 2 ，e3 个 3 ，e5 个 5。
        // 当 k 去除这些所有的因数之后结果为 1 则刚好除尽，不为 1 ，则还有其他的因数，并且该因数一定大于 6 ，不满足题目要求的范围
        return {tuple(e2, e3, e5), k==1};
    }

    int countSequences(vector<int>& nums, long long k) {
        auto [e, ok] = primeFactorization(k);
        // k 是否含有大于 5 的质因子
        if (!ok) return 0;

        int n = nums.size();
        vector<tuple<int,int,int>> es(n); 
        // 缓存存储每个数对应的质因数的幂（可以直接穷举映射，减少运算次数）
        for (int i=0; i<n; ++i) es[i] = primeFactorization(nums[i]).first;

        unordered_map<int,int> memo; // 临时缓存，记录相同状态，减少运算次数

        // lambda 表达式定义 dfs 函数
        auto dfs = [&](this auto&& dfs, int i, int e2, int e3, int e5) -> int {
            // 终止标志，当遍历结束时，初始值 val 应该为 1 ，幂全为 0 ，
            // 当全为 0 时，说明当前的 dfs 搜索方式可行，返回 1 种结果，不全为 0 ，则不可行，返回 0 。
            if (i<0) return e2==0 && e3==0 && e5==0; 

            // 把 i,e2,e3,e5 状态参数编码成 int 唯一标识符，类似摘要算法（记录缓存）
            int key = i<<21 | (e2+n*2)<<14 | (e3+n)<<7 | (e5+n);

            // 优先使用缓存
            auto it = memo.find(key); 
            if (it != memo.end()) return it->second;

            // 没有缓存
            auto [x, y, z] = es[i]; // 当前数字的幂
            int res1 = dfs(i-1, e2-x, e3-y, e5-z); // 倒推的除法运算
            int res2 = dfs(i-1, e2+x, e3+y, e5+z); // 倒推的乘法运算
            int res3 = dfs(i-1, e2, e3, e5); // 不变
            int res = res1 + res2 + res3; // 运算到当前下标 i 时的可行结果数 

            memo[key] = res; // 添加缓存
            return res;
        };

        auto [e2, e3, e5] = e;
        return dfs(n-1, e2, e3, e5); // 递归dfs搜索结果，从后往前传递，从前往后返回最终结果
    }
};
```

```cpp
class Solution {
public:
    int size;
    vector<tuple<int,int,int>> flags;
    unordered_map<int,int> mp;
    tuple<int, int, int> primeFactorization(long long k) {
        int e2=0,e3=0,e5=0;
        
        while(k%2==0) {
            ++e2;k/=2;
        } 
        while(k%3==0) {
            ++e3;k/=3;
        }
        while(k%5==0) {
            ++e5;k/=5;
        }

        return make_tuple(e2,e3,e5);
    }

    int dfs(int i, int e2, int e3, int e5) {
        if (i < 0) return e2 == 0 && e3 == 0 && e5 == 0;

        int key = (e5+size) | (e3+size*2)<<7 | (e2+size*2)<<14 | (i<<21);
        auto it = mp.find(key);
        if (it != mp.end()) return it->second;

        auto [a2, a3, a5] = flags[i];
        int res1 = dfs(i-1, e2-a2, e3-a3, e5-a5);
        int res2 = dfs(i-1, e2+a2, e3+a3, e5+a5);
        int res3 = dfs(i-1, e2, e3, e5);
        int res = res1 + res2 + res3;

        mp[key] = res;

        return res;
    }

    int countSequences(vector<int>& nums, long long k) {
        auto [e2,e3,e5] = primeFactorization(k);
        if (k != (long long)(pow(2,e2) * pow(3,e3) * pow(5, e5))) return 0;

        size = nums.size();
        flags.resize(size);
        for (int i=0; i<size; ++i) flags[i] = primeFactorization(nums[i]);

        return dfs(size-1, e2, e3, e5);
    }
};
```



# 训练赛


## 第 491 场周赛 2026/03/01


[3856. 移除尾部元音字母 - 力扣（LeetCode）](https://leetcode.cn/problems/trim-trailing-vowels/)

[3857. 拆分到 1 的最小总代价 - 力扣（LeetCode）](https://leetcode.cn/problems/minimum-cost-to-split-into-ones/)

[3858. 按位或的最小值 - 力扣（LeetCode）](https://leetcode.cn/problems/minimum-bitwise-or-from-grid/)

[3859. 统计包含 K 个不同整数的子数组 - 力扣（LeetCode）](https://leetcode.cn/problems/count-subarrays-with-k-distinct-integers/)







```cpp

```





## <font style="color:rgb(26, 26, 26);">第 177 场双周赛 2026/02/28</font>
### 
[101001. 不同频率的最小数对 - 力扣（LeetCode）](https://leetcode.cn/problems/smallest-pair-with-different-frequencies/)

[100792. 合并靠近字符 - 力扣（LeetCode）](https://leetcode.cn/problems/merge-close-characters/)

[100990. 使数组奇偶交替的最少操作 - 力扣（LeetCode）](https://leetcode.cn/problems/minimum-operations-to-make-array-parity-alternating/)

[101002. 给定范围内 K 位数字之和 - 力扣（LeetCode）](https://leetcode.cn/problems/sum-of-k-digit-numbers-in-a-range/)



比赛情况：只 AC 了第一题



```cpp
class Solution {
public:
    vector<int> minDistinctFreqPair(vector<int>& nums) {
        int x = -1;
        int y = -1;
        vector<int>arr(150);
        int size = nums.size();
        if (size <=1) return {x,y};
        
        for (int i=0; i<size; ++i) ++arr[nums[i]];


        for (int i=0; i<=100; ++i) {
            if (arr[i]==0) continue;
            if (x==-1) {
                x=i;
                continue;
            }
            if (y==-1 && arr[i]==arr[x]) continue;
            y=i;
            break;
        }
        if (x==-1 || y==-1) return {-1,-1};
        return {x,y};
    }
};
```

```cpp
// 我的第一直觉做法太复杂了，为了解决后面的字符偏移，
// 		专门设置了一个 offset 偏移变量来计算相对位置，增加了考虑的复杂度
// 题解做法很巧妙，指针构造答案，通过追加的形式判断，从原始字符串中取字符
// 		追加到当前的结果中去，末尾的坐标就是偏移后的坐标，每个坐标都是真实的，不需干预，自动计算
// 		直接把我的 offset 秒了

class Solution {
public:
    string mergeCharacters(string s, int k) {
        int pos[26]{};
        fill(pos, pos + 26, INT_MIN / 2);
        int top = 0;
        for (char& c : s) {
            if (top - pos[c - 'a'] > k) {
                pos[c - 'a'] = top;
                s[top++] = c;
            }
        }
        s.resize(top);
        return s;
    }
};
```

```cpp
class Solution {
public:
    vector<int> makeParityAlternating(vector<int>& nums) {
        if (nums.size() == 1) {
            return {0, 0};
        }

        int g_min = ranges::min(nums);
        int g_max = ranges::max(nums);

        auto calc = [&](int target) -> vector<int> {
            int op = 0;
            int mn = INT_MAX, mx = INT_MIN;
            for (int i = 0; i < nums.size(); i++) {
                int x = nums[i];
                // 如果 target = 0，那么操作后，nums 每个数的奇偶性必须分别等于 0,1,0,1,... 即 target ^ (i%2)
                if (((x - i) & 1) != target) { // 等价于 (x&1) != (target ^ (i%2))
                    op++;
                    if (x == g_min) {
                        x++;
                    } else if (x == g_max) {
                        x--;
                    }
                }
                mn = min(mn, x);
                mx = max(mx, x);
            }
            return {op, max(mx - mn, 1)}; // 在 n >= 2 的情况下，极差至少是 1
        };

        return min(calc(0), calc(1));
    }
};
```

```cpp
// 细节：取模运算，多处取模，防止溢出；用 long long 存结果，最后返回 int。
// 先把计算公式推导出来，再看有没有可以简便的地方，在什么地方可能要取模避免溢出
class Solution {
    static constexpr int MOD = 1'000'000'007;

    long long pow(long long x, int n) {
        // 快速幂运算
        long long res = 1;
        for (; n; n /= 2) {
            if (n % 2) {
                res = res * x % MOD;
            }
            x = x * x % MOD;
        }
        return res;
    }

public:
    int sumOfNumbers(int l, int r, int k) {
        int m = r - l + 1;
        return (l + r) * m * (pow(10, k) - 1 + MOD) % MOD * pow(18, MOD - 2) % MOD * pow(m, k - 1) % MOD;
    }
};

```



# 章节训练


[分享丨【算法题单】位运算（基础/性质/拆位/试填/恒等式/思维） - 讨论 - 力扣（LeetCode）](https://leetcode.cn/discuss/post/3580371/fen-xiang-gun-ti-dan-wei-yun-suan-ji-chu-nth4/)





