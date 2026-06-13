> 【黑马程序员新版Spring零基础入门到精通，一套搞定spring全套视频教程（含实战源码）】https://www.bilibili.com/video/BV1rt4y1u7q5?p=6&vd_source=b6e1ca78539fba73d35a26224eac9099
>
> 



降低代码的耦合度，为什么：

- 程序代码中不要手动 new 对象，第三方根据要求为程序提供需要的 Bean 对象
  1. IoC 思想（Inversion of control）：控制反转，强调的是原来在程序中创建 Bean 的权利反转给第三方
  2. DI 思想（Dependency Injection）：依赖注入，强调的 Bean 之间关系，这种关系第三方负责去设置
  3. AOP 思想（Aspect Oriented Programming）：面向切面编程，功能的横向抽取，主要的实现方式就是 Proxy
