### 我遇到的BUG





问题：提示词加载失败。网络传输，Java默认解析器读取失败，Jinja。不能读取JSON。
解决方案：一步一步的保证每个阶段正常工作。防止黑箱太多，无法找到问题根源，保证一个步骤正确。



问题：
火山引擎的api在配置claude跟springAI时均报错，说无法通过验证。
解决方案：
暂时无。更换成deepseek就行了。火山引擎使用的模型也是deepseek但是就是不行，接口有兼容openAI格式的。



问题：
SpringAI包与Springboot版本冲突。SpringAI2与springboot4。
解决方案：
回退到SpringAI1的版本，稳定版。



mysql登录账户不行。   redis写配置开放端口使用文件覆盖。    nginx





VibeCoding 乱码问题。







Git 乱码

![](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260413154817912.png)





外接 api 使用。

阿里云的 oss 对象存储服务，api 操作，通过 ai 客服自动生成工具类代码进行使用，减少人工学习成本





python，响应为 null

解决结果：端口被占用了，线程没有及时断开连接。Pycharm 只是把终端窗口关闭了，并没有断开连接，导致接口一直是旧的接口

搭建的新接口没有被更新，一直 null 

多个程序监听了同一个端口

![image-20260414092812100](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20260414092812100.png)

![image-20260414092753326](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260414092753326.png)





---

赛事是赛事，标签是标签

```
赛事既可以是一个简单的标签，也可以是一个完整的赛事表。概念混淆了
标签中的赛事可以不一定非得跟赛事表中对应啊，我只是为了打个标签，没必要将题目与那个赛事表建立强关联啊，我只需要一个标签足以，筛选的时候也只需要使用标签就行了，不用完整的赛事实体啊。这并不冲突
```

我经历的阶段：

1. 一个一个字段的映射。很多标签
2. 把每个标签改为通用的 List 接收，分为已经有的，以及待创建的
3. 把所有标签统一list接收，不分类，有id的就是已经存在的，没有的就是需要新建的

