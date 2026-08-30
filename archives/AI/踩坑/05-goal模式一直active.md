使用 claude code 的之后，设置了一个非常复杂的任务，但是 AI 解决不了的时候或者被用户中途打断不执行的之后，最初设立的任务都没有完成，导致整个会话一直不会自动结束，一直在等待指示，一直在思考，因为 goal 模式不会主动停止中断会话，就算我中途说了停止任务，但是最初设置的目标 goal 没有完成，那么这个会话就一直处于 goal active 状态，会话不会中断，一直在思考然后回复，直到完成最高优先级最初的 goal 。

代码就类似于：

```
while (isNotFinished(goal)) {
	chat()  // 只要任务没完成，中途用户输入什么内容，都是不会主动中断的，只是会不停的回复同一个内容，浪费 token。
}
```



![image-20260803162058031](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260803162058031.png)



![image-20260803171732849](https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/image-20260803171732849.png)