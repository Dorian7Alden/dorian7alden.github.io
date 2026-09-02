# 注解


`@Value("${variable}")`

给变量加注解

自定义配置application.yml信息获取

```java
@Value("${email.name}")
public String name;
```

也可以运用在方法传参列表里面，自动读取







# Lombok
> 工具库。<font style="color:rgba(0, 0, 0, 0.85);">在</font>**编译期**<font style="color:rgba(0, 0, 0, 0.85);">自动生成 Java 类中常见的样板代码</font>
>

```xml
<dependency>
  <groupId>org.projectlombok</groupId>
  <artifactId>lombok</artifactId>
</dependency>
```

+ `@Data`
    - 为实体类自动生成 getter()、setter()、toString()等方法
+ `@NoArgsConstructor`
    - 生成无参数的构造方法
+ `@AllArgsConstructor`
    - 生成全参数的构造方法





# Spring Validation
> 对注册接口的参数进行合法性校验
>

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

**校验使用：**（正则表达式进行校验）

1. 引入依赖
2. 在 Controller 类上添加`@Validated`注解
3. 在参数前面添加`@Pattern`注解

```java
@RestController
@RequestMapping("/user")
@Validated
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/register")
    public Result register(@Pattern(regexp = "^\\S{5,16}$") String username,
                           @Pattern(regexp = "^\\S{5,16}$") String password) {

        User user = userService.findByUserName(username);

        if (user != null) return Result.error(("用户名已存在，注册失败"));

        userService.register(username, password);
        return Result.success();
    }

}
```

**参数校验失败异常处理：**

1. 创建一个 exception 包
2. 创建一个 GlobalExcepionHandler 类

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(Exception.class)
    public Result handleException(Exception e) {
        e.printStackTrace();
        // 并不是每个异常类都封装了getMessage()方法
        return Result.error(StringUtils.hasLength(e.getMessage())? e.getMessage() : "操作失败");
    }

}
```





# java-jwt
> JWT 工具类
>

```xml
<dependency>
  <groupId>com.auth0</groupId>
  <artifactId>java-jwt</artifactId>
  <version>4.4.0</version>
</dependency>
```









# 依赖
## SpringWeb
```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```





## Mybatis
```xml
<dependency>
  <groupId>org.mybatis.spring.boot</groupId>
  <artifactId>mybatis-spring-boot-starter</artifactId>
  <version>3.0.3</version>
</dependency>
```





## MySQL
```xml
<dependency>
  <groupId>com.mysql</groupId>
  <artifactId>mysql-connector-j</artifactId>
</dependency>
```



























