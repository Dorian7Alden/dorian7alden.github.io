### 问题

在传统 JavaWeb 项目中正确配置了相关的 xml 文件，但是还是无法访问对应的资源

问题原因：artifact 没有把 Spring 依赖库打包到 WEB-INF/lib/，导致 Tomcat 无法加载 DispatcherServlet。 



### 解决



    1. 创建了 web/WEB-INF/lib/ 目录 并复制了 50 个 jar 包（排除了 javadoc 和 sources）
    2. 修改了 artifact 配置 (.idea/artifacts/ee_middle_Web_exploded.xml)，让 IntelliJ 知道要把 lib/ 包含进构建产物

  现在在 IntelliJ 中 Rebuild Artifact，然后重启 Tomcat，http://localhost:8080/index 应该就能正常显示了。



在没有 Maven/Gradle 的传统 Java Web 项目中，确实需要"配置两次"：

两个阶段的区别

![image-20260528151315183](https://gitee.com/Seniorsy/pic-go/raw/master/typora/image-20260528151315183.png)



如何避免重复？

  迁移到 Maven 可以一步解决。只需一个 pom.xml，声明：

```
<dependency>
  <groupId>org.springframework</groupId>
  <artifactId>spring-webmvc</artifactId>
  <version>4.3.2.RELEASE</version>
</dependency>
```

  Maven 会自动：
  - 让 IntelliJ 识别依赖（编译时）
  - 打包进 WEB-INF/lib/（运行时）

  你现在的情况

  刚才我已经帮你把 jar 从 ../libs/ 复制到了
  web/WEB-INF/lib/，编译时依赖（.iml）本来就已经指向 ../libs/，所以你现在：

  - 不需要再手动拖任何东西，两边的 lib 依赖都已就绪
  - 只需要在 IntelliJ 里 Rebuild Artifact，然后重启 Tomcat 即可

