> 注意：B 站上关于 Tomcat 的教程大多是提升的进阶教程，关于底层原理相关的，不适合初学者看，能用，会配置就直接学 Servlet
>
> 学习资料 - 快速入门
>
> 【Tomcat极速入门】https://www.bilibili.com/video/BV12H4y1W7ic?p=3&vd_source=b6e1ca78539fba73d35a26224eac9099
>
> 大概 1h 左右，语速较慢，但是讲得很好。建议 3 倍速
>
> 课程目录：
>
> - 引言、Tomcat 介绍、配置
> - 启动、关闭、常见问题
> - 部署项目方式1/2/3
> - URL 与 URI 的概念
>
> 视频看完之后，还需要学会，如何在 IDEA 中关联 Tomcat 。需要梳理清楚项目类型：Java 项目 <=> Web 项目
>
> 【7.idea关联tomcat及web项目创建部署】https://www.bilibili.com/video/BV141421d71E?vd_source=b6e1ca78539fba73d35a26224eac9099
>

​	

> 补充：
>
> - 建立先熟悉一下 IDEA 的 Project Structure 的相关信息
>
> - Tomcat 服务器最好不要放在中文路径下，启动日志里面会有 warning 
> - 解决日志乱码需要在 logging.properties 中修改所有的 utf-8 为 gbk 



# 学习顺序



1. Tomcat 的介绍，什么是 Tomcat ，用来干嘛的
2. 如何启动 Tomcat 
3. 如何手动部署 Tomcat 
4. 如何将 IDEA 关联 Tomcat 



自此， Tomcat 的搭建就到此结束了，服务器软件部署完成，可以开始学习如何写代码了。至于 Tomcat 的其他内容，皆是进阶内容，了解 Tomcat 的底层原理等等等等，初学者了解即可，暂时不必掌握。



# IDEA 关联 Tomcat 流程



> 步骤 1 是在**创建**项目
>
> 步骤 2 是在**输出**项目编译后的产品
>
> 步骤 3 是在**部署**编译后的产品



1. 创建一个 web 项目

   1. 创建 Java 模块

   2. 创建 Web 模块

      <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260117022033019.png" alt="image-20260117022033019" style="zoom:50%;" />

2. 根据模块创建一个 artifacts （编译之后的项目，即 out 目录下的内容，IDEA 会将该 artifacts 的内容连接到 Tomcat 的应用的文件夹下，从而建立连接，可以直接部署 web 应用，要不然就得手动操作，部署应用）

   ![image-20260117021324172](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260117021324172.png)

3. 部署项目：配置启动项，通过 Tomcat 启动项目，配置启动

   <img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260117020914320.png" alt="image-20260117020914320" style="zoom: 50%;" />

4. 在 web 目录下创建前端文件（WEB-INF 目录下的资源是禁止访问的资源）











# 底层解析 - 暂时没必要深入



## 总体架构



### Container设计



---

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260110143527860.png" alt="image-20260110143527860" style="zoom:50%;" />

---



### Connector设计



---

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260110144526650.png" alt="image-20260110144526650" style="zoom:50%;" />

---



---

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260110144535751.png" alt="image-20260110144535751" style="zoom:50%;" />

---



### 最终设计



---

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260110145529903.png" alt="image-20260110145529903" style="zoom:50%;" />

---



### 组件说明



---

![image-20260110150220223](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260110150220223.png)

---



### 启动过程



---

![image-20260110151039178](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260110151039178.png)

---





