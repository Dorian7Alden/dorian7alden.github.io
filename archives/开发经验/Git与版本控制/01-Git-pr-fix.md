## 2026-05-08



![66e3b816-2293-457a-8e5e-41a37513d50d](https://gitee.com/Seniorsy/pic-go/raw/master/typora/66e3b816-2293-457a-8e5e-41a37513d50d.png)



### Context



我提交了一个 pr 之后，代码中发现了错误的修改，需要被打回修复。当我修复了之后，再次提交代码的时候，不知道怎么提交。





### Question



疑问：直接 commit 是在原来的分支上进行提交，对 pr 会有影响吗？怎么同步更新 pr 呢？

这里的 Amend 是什么意思？怎么理解？



### Answer



**继续在同一个分支上修改**，PR 会自动更新：GitHub、GitLab 等平台会检测到分支有新的提交（或强制推的改动），PR 页面会立刻同步你修复后的代码，维护者就能看到更新后的差异，并重新进行审查。

**总结**：在原有分支上改完、推送，PR 自动更新，直接通知 reviewer 重新审查即可。



---



`git commit --amend` **不会新增一个 commit 记录**，而是**修改最近的一次 commit**（替换掉它）。
它会将你**当前暂存区的内容**与上一次 commit 的内容合并，并允许你**重新编辑 commit 信息**。



**具体效果**：

- 原 commit 被丢弃，生成一个**新的 commit**（但 commit ID 会变）。
- 历史中看起来还是只有那一个 commit，没有多余的“修复记录”。
- 如果已经推送到远程分支（比如 PR 对应的分支），需要 `git push --force`（或 `--force-with-lease`）才能覆盖远程分支。

