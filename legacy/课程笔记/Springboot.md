

> 【黑马程序员SpringBoot3+Vue3全套视频教程，springboot+vue企业级全栈开发从基础、实战到面试一套通关】[https://www.bilibili.com/video/BV14z4y1N7pg?p=7&vd_source=b6e1ca78539fba73d35a26224eac9099](https://www.bilibili.com/video/BV14z4y1N7pg?p=7&vd_source=b6e1ca78539fba73d35a26224eac9099)
>



#  基础篇-06 springboot整合mybatis  


1. 配置pom
    1. 配置在父级的dependencies结点下
    2. 配置mybatis起步依赖

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.0</version>
</dependency>
```

    3. mysql数据库驱动依赖

```xml
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>9.2.0</version>
</dependency>
```

2. 刷新pom配置构建项目
3. 配置application.yml

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/springboot
    username: root
    password: 44448888
```







# 基础篇-07_Bean 扫描


+ 标签：<context:component-scanbase-package="com.itheima"/>
+ 注解：@ComponentScan(basePackages="com.itheima")





# 基础篇-08_Bean 注册






注册的方式：

+ @Bean
+ @Import



听不懂



手动实现：读取手动写的文件配置



IOC 容器。Bean 注册

我的理解：导入第三方类



# 基础篇-09_Bean 注册条件


不明所以









# 基础篇-10_ 自动配置原理




定义：遵循约定大约配置的原则，在boot程序启动后，起步依赖中的一些bean对象会自动注入到ioc容器

原理：

1. 在主启动类上添加了SpringBootApplication注解,这个注解组合了EnableAutoConfiguration注解
2. EnableAutoConfiguration注解又组合了Import注解,导入了AutoConfigurationImportSelector类
3. 实现selectImports方法,这个方法经过层层调用,最终会读取META-INF 目录下的 后缀名 为imorts的文件,当然了,boot2.7以前的版本,读取的是spring.factories文件,
4. 读取到全类名了之后,会解析注册条件,也就是@Conditional及其衍生注解,把满足注册条件的Bean对象自动注入到IOC容器中





# 基础篇-11_ 自定义 starter






# 实战篇-01_ 实战概述


**项目名称**：大事件

**项目架构**：

+ 后端：
    - Validation
    - Mybatis
    - Redis
    - Junit
    - 项目部署
+ 前端：
    - Vite
    - Router
    - Pina
    - Element-Plus

**需求**：

+ 用户：
    - 注册
    - 登录
    - 获取用户详细信息
    - 更新用户基本信息
    - 更新用户头像
    - 更新用户密码
+ 文章分类：
    - 文章分类列表
    - 新增文章分类
    - 更新文章分类
    - 获取文章分类详情
    - 删除文章分类
+ 文章管理：
    - 新增文章
    - 更新文章
    - 获取文章详情
    - 删除文章
    - 文章列表(条件分页)
+ 文件上传



# 实战篇-02_ 开发模式和环境搭建


步骤：

1. 执行资料中的big_event.sql脚本，准备数据库表
2. 创建springboot工程，引入对应的依赖（web、mybatis、mysql驱动）

```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>3.5.3</version>
</parent>
```

```xml
<dependencies>

  <!-- web依赖 -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  
  <!-- mybatis依赖 -->
  <dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.0</version>
  </dependency>
  
  <!-- mysql驱动依赖 -->
  <dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
  </dependency>

</dependencies>
```

3. 配置文件application.yml中引入mybatis的配置信息

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/big_event
    username: root
    password: 44448888
```

4. 创建包结构，并准备实体类

```plain
- package
  - controller
  - mapper
  - pojo
  - service
    - iml
  - utils
  - BigEventApplication.java
```







# 实战篇-03_ 注册接口


用户

+ 注册
+ 登录
+ 获取用户详细信息
+ 更新用户基本信息
+ 更新用户头像
+ 更新用户密码



:::info
**lombok 依赖**

在编译阶段，为实体类自动生成 setter、getter、toString 等方法

在 pom 文件中引入依赖，再在实体类上添加`@Data`注解即可

:::

```xml
<dependency>
  <groupId>org.projectlombok</groupId>
  <artifactId>lombok</artifactId>
</dependency>
```



```xml
明确需求 --> 阅读接口文档 --> 思路分析 --> 开发 --> 测试
```



```json
{
  "code": 0;
  "message": "";
  "data": null
}
```

因此，可以开发一个 result 实体类用来接收这个返回的数据



:::info
遇到的问题：**依赖版本不兼容**

<font style="color:rgba(0, 0, 0, 0.85);">Spring Boot 3.5.3 与 mybatis-spring-boot-starter:3.0.0 不兼容，导致 mapper 映射失败</font>

<font style="color:rgba(0, 0, 0, 0.85);">将 mybatis-spring-boot-starter 的版本改为 3.0.3 即可</font>

:::



三层架构实现接口：

+ Controller：定义接口
+ Service：业务逻辑
+ Mapper：映射数据





# 实战篇-04_ 注册接口参数校验


使用 Validation 框架完成







# 实战篇-05_ 登录主逻辑


```java
@PostMapping("/login")
public Result  login(@Pattern(regexp = "^\\S{5,16}$") String username,
                     @Pattern(regexp = "^\\S{5,16}$") String password){
    //根据用户名查询User
    //判断是否查询到
    //判断密码是否正确
}
```



```java
@PostMapping("/login")
public Result<String> login(@Pattern(regexp = "^\\S{5,16}$") String username,
                            @Pattern(regexp = "^\\S{5,16}$") String password) {

    User user = userService.findByUserName(username);

    if (user == null) return Result.error("用户不存在，请先注册");
    if (!Md5Util.getMD5String(password).equals(user.getPassword())) return Result.error("密码错误");

    return Result.success("JWT session");
}
```



# 实战篇-06_ 登录认证引入


问题：在未登录的情况下，可以访问到其他资源

解决：令牌。就是一段字符串

令牌：

+ 承载业务数据，减少后续请求查询数据库的次数
+ 防篡改，保证信息的合法性和有效性

最常用的令牌规范：JWT



# 实战篇-07_ JWT 令牌


简介：

+ 全称：JSON Web Token （[点击查看完整信息](http://jwt.io)）
+ 定义了一种简洁的、自包含的格式，用于通信双方以 json 数据格式安全的传输信息。
+ 组成：
    - 第一部分：Header（头），记录令牌类型、签名算法等。例如：{"alg":"HS256", "type":"JWT"}
    - 第二部分：Payload（有效载荷），携带自定义信息、默认信息等。例如：{"id":"1","username":"Tom"}
    - 第三部分：Signature（签名），防止 Token 被篡改，确保安全性。将 header、payload，并加入指定密钥，通过指定签名算法计算而来。
+ 字符串通过 Base64 编码读取解析

<img src="https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/1761363389500-567538a5-0313-4bb6-be4f-3b78a01ecafa.png" width="1138" title="" crop="0,0,1,1" id="u046fdb5e" class="ne-image">



认证逻辑：

+ `/login`生成令牌
+ `/list`（功能接口）验证令牌



生成令牌：

1. 引入 java-jwt 坐标
2. 引入单元测试坐标

```java
<!-- java-jwt坐标 -->
<dependency>
  <groupId>com.auth0</groupId>
  <artifactId>java-jwt</artifactId>
  <version>4.4.0</version>
</dependency>

<!-- 单元测试的坐标 -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
</dependency>
```

```java
public class JwtTest {

    @Test
    public void testGen() {

        Map<String, Object> claims = new HashMap<>();
        claims.put("id", 1);
        claims.put("username", "ZhangSan");

        String token = JWT.create()
            .withClaim("user", claims) // 添加载荷
            .withExpiresAt(new Date(System.currentTimeMillis() + 1000 * 60 * 10)) // 设置过期时间
            .sign(Algorithm.HMAC256("secret")); // 指定算法，配置密钥

        System.out.println(token);
    }

}
```



验证令牌：

```java
@Test
public void testParse() {
    String token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" +
    ".eyJ1c2VyIjp7ImlkIjoxLCJ1c2VybmFtZSI6IlpoYW5nU2FuIn0sImV4cCI6MTc2MTM2NDk3MX0" +
    ".eZ5c55rL8RpXpz8lqXGo0ZttIbJAQNFGc7ktJBFuoFc";
    // 创建一个验证器
    JWTVerifier jwtVerifier = JWT.require(Algorithm.HMAC256("secret")).build();
    // 验证token，生成一个解析后的JWT对象
    DecodedJWT decodedJWT = jwtVerifier.verify(token);
    Map<String, Claim> claims = decodedJWT.getClaims();
    System.out.println(claims.get("user"));
}
```

验证失败情况：

+ 头部或载荷部分被篡改
+ 密钥被篡改
+ token 过期了



# 实战篇-08_ 登录认证 _ 完成


```java
@PostMapping("/login")
public Result<String> login(@Pattern(regexp = "^\\S{5,16}$") String username,
                            @Pattern(regexp = "^\\S{5,16}$") String password) {

    User user = userService.findByUserName(username);

    if (user == null) return Result.error("用户不存在，请先注册");
    if (!Md5Util.getMD5String(password).equals(user.getPassword())) return Result.error("密码错误");

    // 登录成功
    Map<String, Object> claims = new HashMap<>();
    claims.put("id", user.getId());
    claims.put("username", user.getUsername());

    String token = JwtUtil.genToken(claims);
    return Result.success(token);
}
```



```java
@RestController
@RequestMapping("/article")
public class ArticleController {

    @GetMapping("/list")
    public Result<String> list(@RequestHeader(name = "Authorization") String token, HttpServletResponse response) {
        // 验证token
        try {
            Map<String, Object> claims = JwtUtil.parseToken(token);
            return Result.success("所有文章数据...");
        } catch (Exception e) {
            response.setStatus(401);
            return Result.error("用户未登录");
        }
    }
}
```



拦截器实现自动验证令牌

+ 拦截类：实现 HandlerInterceptor 类的 preHandle 方法
+ 配置类：实现 WebMvcConfigurer 类的 addInterceptors 方法



```java
@Component
public class LoginInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 令牌验证
        String token = request.getHeader("Authorization");
        try {
            Map<String, Object> claims = JwtUtil.parseToken(token);
            return true; // 放行
        } catch (Exception e) {
            response.setStatus(401);
            return false; // 不放行
        }
    }
}
```



```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    // 注册拦截器
    @Autowired
    private LoginInterceptor loginInterceptor;

    // 添加拦截器
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)
        .excludePathPatterns("/user/login", "/user/register");
    }
}
```



:::info
问：@Component 的作用

:::



# 实战篇-09_ 获取用户详细信息


+ Postman 配置脚本，为多个请求添加 header 信息

<img src="https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/1761376884528-9352862d-d5cb-464b-b682-d2a2a8f11c06.png" width="1174.6666666666667" title="" crop="0,0,1,1" id="u978088bd" class="ne-image">



遇到的问题：

+ 返回数据的时候把所有数据，包括敏感数据 password 也返回了
+ 时间类型的数据返回为 null：因为在数据库中是下划线命名，而在 java 实体类中是驼峰命名，匹配不上

解决：

+ `@JsonIgnore`注解，可以将实体类的属性在转换为 json 数据的时候忽略
+ yml 配置`map-underscore-to-camel-case`为 true



:::info
@JsonIgnore 注解是来自 com.**fasterxml.jackson**.annotation.JsonIgnore 这个包

:::









# 实战篇-10_ 获取用户详细信息 _ThreadLocal 优化


ThreadLocal 的优点：

+ 线程安全
+ 不同的线程的数据互不干扰
+ 减少参数的传递
+ 同一个线程共享数据



```java
public class ThreadLocalTest {

    @Test
    public void testThreadLocal() {

        ThreadLocal tl = new ThreadLocal();

        new Thread(() -> {
            tl.set("萧炎");
            System.out.println(Thread.currentThread().getName() + ": " + tl.get());
            System.out.println(Thread.currentThread().getName() + ": " + tl.get());
            System.out.println(Thread.currentThread().getName() + ": " + tl.get());
        }, "蓝色").start();

        new Thread(() -> {
            tl.set("药尘");
            System.out.println(Thread.currentThread().getName() + ": " + tl.get());
            System.out.println(Thread.currentThread().getName() + ": " + tl.get());
            System.out.println(Thread.currentThread().getName() + ": " + tl.get());
        }, "绿色").start();
    }

}
```



使用 ThreadLocal 进行优化：

+ 这个 ThreadLocal 对象为全局对象，使拦截器方法跟数据请求方法都能同时访问到
+ 在拦截器中，将负载 add 到 ThreadLocal 中，在请求的时候直接从 ThreadLocal 中使用 get 方法读取数据
+ 读取完数据之后，再通过拦截器的 afterCompletion 方法释放资源，防止内存泄漏



# 实战篇-11_ 更新用户基本信息


+ 更新数据一般用 PUT 方法
+ 传参用 json。在 controller 里面参数需要加 @RequestBody 注解



# 实战篇-12_ 更新用户基本信息 _ 参数校验


> Validation 完成了传参的数据校验（用户输入）
>



实体类参数完成校验：（注解）

+ 通过在实体类的属性上添加注解实现
    - `@NotNull`值不能为 null
    - `@NotEmpty`值不能为 null，且不为空。（不为空字符串）
    - `@Email`满足邮箱格式
    - `@Pattern(regexp="")`自定义验证
+ 在需要检验的实体类传参时添加`@Validated`注解



# 实战篇-13_ 更新用户头像


+ 请求方式：Patch（更新其中的部分数据用 Patch）
+ controller 传参的时候添加注解 @RequestParam （接口文档声明了传参方式）
+ 通过注解 @URL 验证 String 数据为一个地址



# 实战篇-14_ 更新用户密码


+ 验证密码参数完整性
+ 验证旧密码是否正确
+ 验证新密码两次同样
+ 先获取到旧密码验证是否正确
+ 更新密码的时候要转 md5



# 实战篇-15_ 新增文章分类


+ 在实现接口的时候，前端并不一定会返回所有的数据。例如：创建时间等可以由后端在 service 层补充

```java
@Service
public class CategoryServiceImpl implements CategoryService {
    @Autowired
    private CategoryMapper categoryMapper;

    @Override
    public void add(Category category) {
        // 补充字段数据
        Map<String, Object> map = ThreadLocalUtil.get();
        Integer userId = (Integer) map.get("id");
        category.setCreateUser(userId);

        category.setCreateTime(LocalDateTime.now());
        category.setUpdateTime(LocalDateTime.now());

        categoryMapper.add(category);
    }
}
```



:::info
报错：No static resource category. 

含义：没有对应的 controller 接口路径

:::



# 实战篇-16_ 文章分类列表


+ `@JsonFormat`指定 json 返回的时候日期时间格式

```java
@Data
public class Category {
    private Integer id;//主键ID

    @NotEmpty
    private String categoryName;//分类名称

    @NotEmpty
    private String categoryAlias;//分类别名
    private Integer createUser;//创建人ID

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;//创建时间
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;//更新时间
}
```



# 实战篇-17_ 获取文章分类详情


+ 在 controller 中，一般方法名就是路径名

```java
@GetMapping("/detail")
    public Result<Category> detail(Integer id) {
        Category category = categoryService.findById(id);
        return Result.success(category);
    }
```

说明：路径为“/detail”，方法名为“detail”，调用的服务为“findById”



# 实战篇-18_ 更新文章分类


+ 更新全部数据用 put 方法
+ 更新部分数据用 patch 方法
+ 发送网络请求的时候，先对请求参数进行校验，如果检验不通过就不提供服务。而不是直接执行服务然后返回报错信息



# 实战篇-19_ 更新文章分类和添加文章分类 _ 分组校验


+ 问题：validation 校验直接写在实体类的属性上，导致全局作用。导致每个请求都必须得满足要求

```java
@Data
public class Category {
    @NotNull
    private Integer id;//主键ID

    @NotEmpty
    private String categoryName;//分类名称

    @NotEmpty
    private String categoryAlias;//分类别名
    private Integer createUser;//创建人ID

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;//创建时间
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;//更新时间
}
```

<img src="https://gitee.com/Dorian7Alden/pic-go/raw/master/typora/1761484308007-dae3bb11-a86b-4855-835b-fb49d3f6fbf5.png" width="1402.6666666666667" title="" crop="0,0,1,1" id="u70c0b822" class="ne-image">



+ 分组校验
    1. 定义分组
    2. 定义检验项时指定归属的分组
    3. 校验时指定要校验的分组
+ 注意事项：定义校验项时如果没有指定分组，则属于 Default 分组。分组之间可以继承



+ 自己实现 delete 接口删除文章分类



# 实战篇-20_ 文章管理














# 实战篇-21_









