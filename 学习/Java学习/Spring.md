> 【尚硅谷Spring零基础入门到进阶，一套搞定spring6全套视频教程（源码级讲解）】https://www.bilibili.com/video/BV1kR4y1b7Qc?p=2&vd_source=b6e1ca78539fba73d35a26224eac9099 （看了 2 套尚硅谷的课程“Spring”、“SpringAI”，评价：不如 AI）
>
> https://www.runoob.com/w3cnote/basic-knowledge-summary-of-spring.html （学前看，学后再看）



## Spring 框架学习



### **学习经验**

---

学习之前，先让 AI 给出一个**全局的内容概况**，知道有哪些，然后一个一个循序渐进地突破。不要直接上来就刷 B 站的课，那些课基本上都是 “培训班” 式的课，教你怎么做，很少教你为什么这么做，学完了还是懵逼的，而且有些课程都不完整，速成课。

> Prompt：
>
> ```prompt
> 【学者角色背景】【任务】【角色定义】
> 【框架|生态】【全局认知】【所有内容|大纲】【关键|必学|进阶|了解】
> 【踩过坑的|经验丰富的|老师】【常见弯路、误区】【内容通俗易懂|辅助理解】
> 【结构清晰层次分明】
> ```

先**认识知识点**，然后再掌握知识点。不要无脑刷！不要无脑刷！不要无脑刷！

**AI** 给的知识也不一定都是对的！准确性待定

学习还是**循序渐进**的**系统**学，最好。

看不懂就**多看帖子**，看别人学完之后分享的理解。学习路线找好了，学习方式可以灵活结合，图书、帖子、视频、文档、AI 等等

看**官方文档**就是最好的学习方式，尤其是**源代码**中的注释说明，有助于理解。如果官方文档写得一坨，那一定不是主流技术。

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260406185813034.png" alt="image-20260406185813034" style="zoom: 67%;" />



### 学习目标

---

学会利用 IoC 容器管理 **Bean**：

- **定义** Bean 的 3 种方式：注解 (@Component)、Java 配置 (@Configuration)、XML 配置（**抛弃**）
- **注入** Bean 的 3 种方式：构造函数注入（**推荐**）、Setter 注入、字段注入 (@Autowired)

创建对象：反射机制（@Component） | 方法中自己 new （@Configuration）



Spring 容器的核心思想：

- **IoC (控制反转)** 将对象创建权从代码转移到容器；**DI (依赖注入)** 是 IoC 的实现方式，容器自动注入依赖对象。

> 依赖：指的是，在 IoC 容器中，对象之间相关调用，A 对象**需要**使用 B 对象，需要把 B 对象注入到 A 对象中去，这种 “需要” 关系就是两个对象之间的依赖。例：Controller 需要使用 Service ，需要先把 Service 注入到 Controller 中去。



理解层面：为什么需要 IoC 容器？……（背八股文即可）



### 前置概念



**Spring Bean**：被 Spring 容器管理的 Java 对象，就是 Bean；

**IoC 容器**：Spring 的「对象**工厂**」，负责**创建**、销毁、**注入**所有 Bean，不用我们手动管理对象。



**Spring 找 Bean 的机制**

---

- **第一步：按「类型」找** ByType
  - 先在 IoC 容器里找**和你要注入的类型完全一致 / 是它子类 / 实现它接口**的 Bean。

- **第二步：按「名称」找** ByName
  - 如果同一种类型的 Bean 有**多个**，Spring 就会再按**Bean 名称**匹配。




**什么是「Bean 名称」？**

---

Bean 都有一个唯一名字，默认规则：

- **@Component 修饰的类**	Bean 名 = **类名首字母小写	**例：`MyUtils` → Bean 名 `myUtils`
- **@Bean 修饰的方法**	Bean 名 = **方法名**

- 情况 1：同类型只有 1 个 Bean → 只看类型就够

- 情况 2：同类型有多个 Bean → 必须按名称匹配

  - 你必须让**变量名 = Bean 名**。或者用 `@Qualifier` 明确指定名称


> 可以在注解中自定义名称：@Component("myBean")     @Bean("customRedisTemplate")
>



### 注解学习



#### 注解清单




##### 一、*核心*关键注解 - 理解运用

|                |             |            |             |
| :------------: | :---------: | :--------: | :---------: |
|   @Component   | @Controller |  @Service  | @Repository |
|     @Value     | @Autowired  | @Qualifier |             |
| @Configuration |    @Bean    |   @Scope   |             |

##### 二、Web 开发注解 - 会用就行了

|                 |                 |                   |                   |
| :-------------: | :-------------: | :---------------: | :---------------: |
| @RestController | @RequestMapping | @ControllerAdvice | @ExceptionHandler |
|   @GetMapping   |  @PostMapping   |    @PutMapping    |  @DeleteMapping   |
|  @RequestParam  |  @PathVariable  |   @RequestBody    |                   |

##### 三、数据库 / 事务注解

```
@Transactional
```

##### 四、进阶可选注解

| AOP 面向切面                     | 配置 / 环境     | **测试**        |
| -------------------------------- | --------------- | --------------- |
| @Aspect                          | @PropertySource | @SpringBootTest |
| @Pointcut                        | @Profile        | @Test           |
| `@Before` / `@After` / `@Around` |                 |                 |



#### @Component (定义 Bean)

---

@Component 是加在**类**上的注解，用来把普通 Java 类交给 Spring 容器管理。

- Spring 会自动扫描带有 @Component 的类，创建对应的 Bean，并放入 IoC 容器统一管理。
- 在三层架构中，通用类用 @Component，业务层 / 控制层 / 持久层通常分别用 @Service / @Controller / @Repository。

> 说明：默认创建的是单例 Bean，不需要自己手动 new 对象。确保 Spring 开启「组件扫描」（SpringBoot 自动开启）



#### @Bean (定义 Bean)

---

@Bean 是写在配置**类方法**上的注解，用来把方法返回的对象交给 Spring 容器管理。

两种使用 @Bean 的方式：

- 标准写法：@Configuration + @Bean（Full 模式）
  - 多次调用，**永远返回同一个单例对象**
  - 适合：第三方 Bean、全局配置、需要单例的 Bean
-  轻量写法：@Component + @Bean（Lite 模式）
  - 每次手动调用会**新建一个对象**
  - 适合：当前组件内部用的简单 Bean，不推荐复杂 / 全局 Bean 这么写

常见运用场景：第三方 jar 包的类（如数据库连接池、线程池、Redis、AI 客户端）

> **@Bean 可以脱离 @Configuration 单独使用**，写在任何被 Spring 管理的类里都行；
>
> 但**规范、正式、全局的 Bean 统一写在 @Configuration 里**，这是行业通用做法；





#### @Component 与 @Bean

---


|    维度    |     @Component      |              @Bean               |
| :--------: | :-----------------: | :------------------------------: |
|   写在哪   |    自己写的类上     |          配置类的方法上          |
| 谁创建对象 | Spring 自动反射创建 |        自己代码 new 返回         |
|  适用对象  |   自己项目里的类    |   第三方类、需要自定义创建的类   |
|   灵活性   |  低，只能自动创建   |          高，可任意配置          |
|   多实例   | 一个类只能一个 Bean | 一个类可创建多个 Bean (多个方法) |
|  注册方式  |      自动扫描       |             手动注册             |



#### @Value

---

专门用于**将外部配置值自动注入到 Spring 管理的 Bean 中**

简单说：把配置文件、环境变量里的参数，自动赋值给 Java 类的变量，不用手动写代码读取配置，解耦代码和配置。

适合**少量、简单、零散**的配置注入，优先用 `@Value`

- 注入方式1：字段注入（简单，不推荐）

  ```java
  @Value("${app.name}")
  private String appName;
  ```

- 注入方式2：构造器注入（官方推荐）

  ```java
  private final String appVersion;
  private final Integer appPort;
  
  // 构造器上形参直接标注 @Value
  public AppConfig(
          @Value("${app.version}") String appVersion,
          @Value("${app.port}") Integer appPort
  ) {
      this.appVersion = appVersion;
      this.appPort = appPort;
  }
  ```

- 注入方式3：Setter注入（太麻烦了，估计没人会这么写）

  ```java
  private List<Integer> idList;
  @Value("${app.ids}")
  public void setIdList(List<Integer> idList) {
      this.idList = idList;
  }
  ```

- 注入资源文件：通过 `@Value("classpath:文件路径")`，直接将 **resources 目录下的文件** 注入为 Spring 的 `Resource` 对象，进而读取文件内容；SpringAI 需要读取提示词的时候，提示词通过 .st 文件存储，通过这种方式加载提示词资源，然后使用（官方推荐）

> - 支持配置默认值、SpEL 表达式，可注入字符串、数字、集合等多种数据类型（自己了解）
> - 不支持注入 static 静态变量
> - 前置条件：
>   - 所属类必须被 Spring 容器管理（需添加 `@Component`/`@Service`/`@Controller`/`@Repository` 等注解）
>   - SpringBoot 默认加载 `application.properties` / `.yml`。自定义配置文件需要加 @PropertySource 注解声明



#### @ConfigurationProperties

---

作用同 @Value 注解。大而整，批量结构化绑定，**企业项目标准用法**。

暂时没必要。



#### @Configuration

---

核心作用只有一个：**把一个 Java 类标记为「Spring 配置类」**，用来**完全替代传统的 XML 配置文件**，让我们用纯 Java 代码配置 Spring 容器、定义和管理 Bean。核心理解：说明书 / 标记

简单说：以前用 `applicationContext.xml` 写 Spring 配置，现在用 `@Configuration` 标记的类写配置。

使用场景：

- **需要手动创建 Bean 时**：第三方库的类、需要自定义初始化参数的类，无法用 `@Component` 自动扫描。
- **想要纯注解开发，不想写 XML 时**：现在 SpringBoot/Spring 主流开发都是纯注解，XML 基本淘汰。
- **需要集中管理多个 Bean 依赖时**：比如配置数据源、事务管理器、MVC 组件等。
- **需要开启 Spring 高级特性时**：必须在配置类上添加 `@EnableXXX` 注解。

1. **整合第三方库、中间件**（数据库、Redis、MQ、OSS、SDK…）
2. **配置 Spring 底层组件**（MyBatis、MVC 拦截器、线程池、事务…）
3. **需要手动 new 对象 + 传参数** 才能用的类
4. **需要开启 Spring 高级功能**（@EnableAsync、@EnableCaching、@EnableScheduling）

> **@Configuration 本质**：是 `@Component` 的**派生注解**，配置类本身也会被 Spring 管理为一个 Bean。



#### @Resource (注入 Bean)

#### @Autowired (注入 Bean)





### 注入 Bean



（插入）**注入 Bean 的最流行做法**（不是无脑 @Autowired ）：**final + @RequiredArgsConstructor**

---

> 官方说明：<u>Field injection</u> is not recommended 不推荐 @Autowired 式的字段注入
>
> The Spring team generally **advocates constructor injection**, as it lets you implement application components as immutable objects and ensures that required dependencies are not null. Furthermore, constructor-injected components are always returned to the client (calling) code in a fully initialized state.
>
> https://www.zhihu.com/question/352403731/answer/2021179686051397939

```java
//=========================自动生成构造函数======================================
@RequiredArgsConstructor // 构造函数注入（推荐做法）
@Service
public class OrderApplicationService { 
    private final OrderDomainService orderDomainService;
    private final TransactionTemplate transactionTemplate;
}
// =======================手写构造器：当注入的对象不是 bean 对象时（例如：注入资源文件。SpringAI注入提示词）====
@Service
public class OpenAppService {
    private final OpenAppMapper openAppMapper;

    public OpenAppService(OpenAppMapper openAppMapper) {
        this.openAppMapper = openAppMapper;
    }
}
```

|      维度      | @Autowired字段注入 |     构造器注入      |
| :------------: | :----------------: | :-----------------: |
|    不可变性    |    不支持final     |      支持final      |
|    单元测试    | 需要反射或启动容器 | 直接new，传Mock对象 |
|   依赖可见性   |  分散在各个字段上  |  集中在构造器参数   |
|   空指针风险   |  运行时可能为null  |   容器启动时校验    |
| Spring官方态度 |         ⚠          |          ✅          |



---



#### 构造器注入（Constructor Injection）（最主流）

```java
@Service
public class UserService {
    // 依赖用 final 修饰，不可变，线程安全
    private final UserDao userDao;

    // Spring 4.3+：只有一个构造器时，**不需要加任何注解**！自动注入
    public UserService(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

####  Setter 方法注入（Setter Injection）

```java
@Service
public class UserService {
    private UserDao userDao;

    // 手动写set方法，无需自动注解
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

#### 字段注入（Field Injection） **不推荐**

```java
@Service
public class UserService {
    // @Resource
    @Autowired
    private UserDao userDao;
}
```



#### 总结

| 注入方式 | 优点 | 缺点 | 适用场景 |
| :--: | ---- | ---- | ---- |
| **构造器注入** | 依赖可声明为 final，不可变、线程安全；依赖强制初始化，无空指针；便于单元测试；依赖关系清晰；无需注解 | 不支持循环依赖 | 绝大多数业务场景，**官方推荐** |
| **Setter 方法注入** | 支持可选依赖、循环依赖；依赖可动态替换 | 依赖可变易被修改；无法用 final；测试不便 | 可选、非必需的依赖 |
| **字段注入（@Autowired/@Resource）** | 写法简洁、代码量少 | 隐藏依赖关系；无法用 final；易空指针；单元测试困难；易导致职责泛滥 | 不推荐用于生产项目 |

- **完全可以不用 `@Autowired` 和 `@Resource`**，它们只是便捷注解，不是必须品
- Spring 依赖注入有 **3 种常用语法**：构造器、Setter、字段（注解）
- （自动 ? 手动）手动注入方式：**XML、JavaConfig、Aware 接口**
- **生产环境唯一推荐：构造器注入**
- 最佳实践：**单个构造器 + final 依赖 + 零自动注解**



