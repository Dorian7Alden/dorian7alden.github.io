## SpringAI 框架学习





### Prompt 

> The Prompt class represents a prompt used in AI model requests. A prompt consists of **one or more messages** and **additional chat options**.

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260405162038219.png" alt="image-20260405162038219" style="zoom:50%;" />

最终大模型发送的是 Prompt 类型的数据，这个 Prompt 可以有 1 条或多条 Message，就是一个消息列表，并且可以携带一下聊天的参数选项。

作用：通过维护 Prompt 可以用来管理上下文





### MessageType

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260405163237337.png" alt="image-20260405163237337" style="zoom:67%;" />

MessageType 共有 4 个类型，分别是：

- user
- assistant
- system
- tool





