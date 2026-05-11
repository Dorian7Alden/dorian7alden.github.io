# 参考资料

> 先看 B 站视频快速了解，再通过文档复习，扩展（图灵官方）
>
> 视频一共 2h ，建议 2 倍速播放

【2026版Maven实战全套教程，这绝对是Maven快速入门到实战教程天花板！】https://www.bilibili.com/video/BV1gJSuBNE3k?p=17&vd_source=b6e1ca78539fba73d35a26224eac9099



[Maven 教程 | 菜鸟教程](https://www.runoob.com/maven/maven-tutorial.html)



Maven 中央仓库：[Maven Repository: Search/Browse/Explore](https://mvnrepository.com/)



# 需要掌握的基本知识

- 创建 Maven 项目
- 项目结构
- 坐标
- 依赖引用
- properties 属性配置
- 创建基于 maven 的 web 应用
- maven 命令
- 依赖范围
- 依赖的传递
- 依赖排除和覆盖
- 聚合工程
- maven 继承



# 验证安装

```
mvn -v  # 应输出 Maven 版本和 Java 信息
```



# 配置 Maven 本地仓库



默认本地仓库路径：

- Windows: `C:\Users\<用户名>\.m2\repository` 
- Linux/macOS: `~/.m2/repository` 

修改仓库位置（可选）：

在 MAVEN_HOME/conf/settings.xml 中修改：

```xml
<localRepository>/path/to/your/repo</localRepository>
```



# 标准 Maven 项目结构



```
my-first-app/
├── pom.xml           # 项目配置文件
├── src/
│   ├── main/         # 主代码
│   │   └── java/     # Java 源代码
│   └── test/         # 测试代码
│       └── java/     # 测试类
```



# pom.xml 解读



```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    
    <!-- 项目坐标（唯一标识） -->
    <groupId>com.example</groupId>      	<!-- 组织名 -->
    <artifactId>my-first-app</artifactId>  	<!-- 项目名 -->
    <version>1.0-SNAPSHOT</version>     	<!-- 版本号 -->

    <!-- 项目打包方式（默认 jar ） ，可选：jar、war、pom、bundle、其他 -->
    <packaging>jar</packaging>
    
    <!-- 定义变量，使用${version.junit}进行引用 -->
    <properties>
    	<version.junit>x.x.x</version.junit>
    </properties>
    
    <!-- 该项目的依赖 --> 
    <dependencies>
        <dependency>
            <groupId>junit</groupId>    
            <artifactId>junit</artifactId>
            <version>4.12</version>
            <!-- 作用范围。默认compile,可选：compile/test/provided/runtime/system -->
            <scope>test</scope> 		
            <optional>false</optional>	<!-- 是否传递依赖。可选 -->
        </dependency>
    </dependencies>
    
    <!-- 在 settings.xml 或 pom.xml 中配置 -->
    <mirror>
        <id>aliyun</id>
        <url>https://maven.aliyun.com/repository/public</url>
        <mirrorOf>central</mirrorOf>
    </mirror>
    
    <!-- 项目名称和 URL（可选） -->
    <name>my-first-app</name>
    <url>http://www.example.com</url>
    
</project>
```



# Maven POM



---

**properties**: 定义项目中的一些属性变量。

用于定义变量，避免重复：

```xml
<properties>
    <java.version>11</java.version>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

---

`repositories`: 仓库配置。

指定远程仓库：

```xml
<repositories>
    <repository>
        <id>aliyun</id>
        <url>https://maven.aliyun.com/repository/public</url>
    </repository>
</repositories>
```

---

`dependencyManagement`: 用于管理依赖的版本，特别是在多模块项目中。

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>5.3.9</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

---

**继承:** 通过 parent 元素，一个POM文件可以继承另一个POM文件的配置：

```xml
<parent>
    <groupId>com.example</groupId>
    <artifactId>parent-project</artifactId>
    <version>1.0-SNAPSHOT</version>
</parent>
```

---

**聚合:** 通过 modules 元素，一个 POM 文件可以管理多个子模块：

```xml
<modules>
    <module>module1</module>
    <module>module2</module>
</modules>
```

---



# POM 标签大全详解



| **标签**                 | **类别** | **说明**             | **示例/可选值**                       | **是否必需**      |
| :----------------------- | :------- | :------------------- | :------------------------------------ | :---------------- |
| **基础信息**             |          |                      |                                       |                   |
| `<modelVersion>`         | 项目结构 | POM模型版本          | `4.0.0`                               | 是                |
| `<groupId>`              | 坐标     | 组织标识（反向域名） | `com.example`                         | 是                |
| `<artifactId>`           | 坐标     | 项目名称             | `my-project`                          | 是                |
| `<version>`              | 坐标     | 项目版本             | `1.0.0-SNAPSHOT`                      | 是                |
| `<packaging>`            | 项目类型 | 打包格式             | `jar`/`war`/`pom`                     | 否（默认jar）     |
| `<name>`                 | 元信息   | 项目显示名称         | `My Application`                      | 否                |
| `<description>`          | 元信息   | 项目描述             | `A demo project`                      | 否                |
| `<url>`                  | 元信息   | 项目主页URL          | `https://example.com`                 | 否                |
| **依赖管理**             |          |                      |                                       |                   |
| `<dependencies>`         | 依赖     | 依赖列表容器         | 包含多个`<dependency>`                | 否                |
| `<dependency>`           | 依赖     | 单个依赖定义         | 包含`groupId`等子标签                 | 可选              |
| `<scope>`                | 依赖     | 依赖作用域           | `compile`/`test`/`provided`/`runtime` | 否（默认compile） |
| `<optional>`             | 依赖     | 是否可选依赖         | `true`/`false`                        | 否（默认false）   |
| `<exclusions>`           | 依赖     | 排除传递性依赖       | 包含`<exclusion>`列表                 | 否                |
| **构建配置**             |          |                      |                                       |                   |
| `<build>`                | 构建     | 构建配置容器         | 包含插件/资源等配置                   | 否                |
| `<plugins>`              | 构建     | 插件列表容器         | 包含多个`<plugin>`                    | 否                |
| `<plugin>`               | 构建     | 单个插件定义         | 需指定`groupId`和`artifactId`         | 可选              |
| `<resources>`            | 构建     | 资源文件配置         | 定义`<resource>`路径                  | 否                |
| `<testResources>`        | 构建     | 测试资源文件配置     | 类似`<resources>`                     | 否                |
| `<finalName>`            | 构建     | 最终打包文件名       | `my-app`                              | 否                |
| **环境配置**             |          |                      |                                       |                   |
| `<properties>`           | 配置     | 自定义变量容器       | 定义键值对                            | 否                |
| `<java.version>`         | 属性     | Java版本变量         | `11`/`17`等                           | 否                |
| `<repositories>`         | 仓库     | 自定义远程仓库列表   | 包含`<repository>`                    | 否                |
| `<pluginRepositories>`   | 仓库     | 自定义插件仓库       | 类似`<repositories>`                  | 否                |
| **多模块管理**           |          |                      |                                       |                   |
| `<modules>`              | 模块     | 子模块列表           | 包含多个`<module>`                    | 聚合项目需要      |
| `<parent>`               | 继承     | 父POM引用            | 需指定父项目坐标                      | 继承项目需要      |
| `<dependencyManagement>` | 依赖     | 统一管理依赖版本     | 定义版本但不引入                      | 否                |
| `<profiles>`             | 配置     | 环境profile容器      | 定义不同环境配置                      | 否                |
| **其他信息**             |          |                      |                                       |                   |
| `<licenses>`             | 法律     | 许可证信息           | 包含`<license>`                       | 否                |
| `<developers>`           | 人员     | 开发者列表           | 包含`<developer>`                     | 否                |
| `<contributors>`         | 人员     | 贡献者列表           | 类似`<developers>`                    | 否                |
| `<issueManagement>`      | 管理     | 问题跟踪系统         | 定义issue系统URL                      | 否                |



