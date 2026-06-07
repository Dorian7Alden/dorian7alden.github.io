### 问题



**传统 JavaWeb 项目必须打包为 WAR**

- 非 Spring Boot 项目没有内嵌 Tomcat，依赖外置容器（如 Tomcat）
- WAR 包有严格的目录结构要求，`WEB-INF`受保护，资源文件必须放在根目录
- 你之前的`pom.xml`写了`<packaging>jar</packaging>`，导致 Tomcat 无法识别 Web 资源

**Jar 包部署的正确方式**

- 若要以 Jar 包形式运行 Web 应用，必须是**Spring Boot 项目**（内置 Tomcat）
- 普通 JavaWeb 项目的 Jar 包只能作为**依赖库**，不能作为 Web 应用本身部署



### 解决方法



修改 `pom.xml` 打包类型，把 `<packaging>jar</packaging>` 改为 `<packaging>war</packaging>`：

```
<packaging>war</packaging>
```

同时，建议添加 `maven-war-plugin` 确保打包正确（如果没有的话）：

```
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-war-plugin</artifactId>
            <version>3.3.1</version>
            <configuration>
                <webResources>
                    <resource>
                        <directory>web</directory>
                    </resource>
                </webResources>
            </configuration>
        </plugin>
    </plugins>
</build>
```