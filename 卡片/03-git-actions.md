



### 切换分支前，用 `git stash` 安全转移未提交的修改

情景描述：

当前我处于 master 分支，对文件进行了**修改**，但是没有 commit 提交修改，希望创建一个新的分支，然后提交内容。

问题：

如果我当前的内容不存起来的话，直接切换分支，会导致当前的仓库加载分支对应的状态，已经修改的文件会被覆盖，由于没有缓存，导致代码丢失

解决方法：

使用 git stash ，将当前的修改存到暂存区，切换分支后，再 git stash pop 取出暂存区的内容，然后进行提交。

![image-20260506020709071](https://gitee.com/Seniorsy/pic-go/raw/master/typora/image-20260506020709071.png)









明白了，您问的是：执行 `git stash pop` 之后，原来在 stash 里的那条记录（比如 `stash@{0}`）还在不在？

**答案：不在了。**

- `git stash pop` = `git stash apply` + `git stash drop`
  它会**应用**最新的 stash 内容到当前工作区，然后**删除**该 stash 条目。
- 如果您想保留 stash 记录方便以后再用，应该使用 `git stash apply`（应用但不删除），之后可以再用 `git stash drop` 手动删除。

> 验证方法：
> 执行 `git stash list` 看看剩下的 stash 列表。如果 pop 之前只有一个条目，pop 之后 `git stash list` 会为空。

所以关于您之前问的“staged 中的缓存还在吗”——您这里指的其实是 **stash 里面保存的修改记录**。
答案是：**pop 之后就不在了**，已经被整体取出来并删除了。



### 创建分支失败

![image-20260506030816373](https://gitee.com/Seniorsy/pic-go/raw/master/typora/image-20260506030816373.png)

![74dada37b512c2ceb461dd4bc1c64f2e](https://gitee.com/Seniorsy/pic-go/raw/master/typora/74dada37b512c2ceb461dd4bc1c64f2e.png)

![image-20260506030753680](https://gitee.com/Seniorsy/pic-go/raw/master/typora/image-20260506030753680.png)