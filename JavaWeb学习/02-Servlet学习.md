> 
>
> 【可能是B站讲的最好的Servlet教程，一天打通Servlet全套教程丨2022最新版，轻松掌握servlet基础+案例实操】https://www.bilibili.com/video/BV1kt4y157xd?p=23&vd_source=b6e1ca78539fba73d35a26224eac9099
>
> 





熟悉 servlet 的 API 文档





### 导包

> Tomcat 11 之后，导入的 servlet 依赖包需要改为 jakarta.servlet 包名改了



```
<dependency>
  <groupId>jakarta.servlet</groupId>
  <artifactId>jakarta.servlet-api</artifactId>
  <version>6.0.0</version>
</dependency>
```



### 配置 Servlet



> 在 web.xml 中对 servlet 进行文件配置



示例一：配置文件配置

![image-20260228145811244](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260228145811244.png)



示例二：注解配置

![image-20260228154018260](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260228154018260.png)





