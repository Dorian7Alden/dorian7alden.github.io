# 何时不应该把 @Value 提取为 @ConfigurationProperties

## 场景描述

在统一配置管理的过程中，我们把 24 个散落的 `@Value` 提取到了 4 个 `@ConfigurationProperties` 类中。但有 2 个 `@Value` 刻意保留了原样：

```java
// MailUtils.java - 保留 @Value
@Value("${spring.mail.from}")
private String from;

// StatisticsController.java - 保留 @Value
@Value("${spring.security.user.password}")
private String password;
```

这不是遗漏，而是有意为之。

## 核心判断标准

| 条件 | 提取为 Property 类 | 保留 @Value |
|------|-------------------|-------------|
| 自定义命名空间（`swu.*`, `weather.*`） | 是 | — |
| Spring Boot 原生命名空间（`spring.*`） | — | 是 |
| 同一 key 在 ≥ 2 个文件中重复 | 是 | — |
| 只在 1 个文件中使用 | 看情况 | 通常保留 |
| 需要跨文件共享同一组配置 | 是 | — |

## 具体案例分析

### 案例 1：`spring.mail.from` — 保留 @Value

**所在的 MailUtils.java：**

```java
@Component
@RequiredArgsConstructor
public class MailUtils {

    private final JavaMailSender mailSender;  // Spring Boot 自动配置的 Bean

    @Value("${spring.mail.from}")
    private String from;                      // 框架原生属性，单点使用

    public void sendMail(String to, String subject, String alias, String htmlContent) {
        InternetAddress addr = new InternetAddress(this.from, alias, "UTF-8");
        // ...
    }
}
```

**不提取的理由：**

1. **归属明确**。`spring.mail.*` 是 Spring Boot 的命名空间，已经被 `MailSenderAutoConfiguration` 读取并配置了 `JavaMailSender` Bean。把它包进自定义的 `MailProperties` 类反而混淆了归属。
2. **单点使用**。只有 `MailUtils` 一处读取 `from` 地址。提取成类只为一个字段，代码量反而增加。
3. **与已有的 Bean 配套**。`from` 和 `mailSender` 来自同一套 Spring Mail 自动配置，放在一起逻辑上一致。
4. **不值得建类**。如果强行提取：

   ```java
   // 不推荐：为一个字段建一个类
   @ConfigurationProperties(prefix = "spring.mail")
   public record MailProperties(String from) {}
   ```
   这个 record 只有一个字段，永远不会扩展（因为 `spring.mail.*` 的其余属性由 Spring Boot 内部管理），创建它的收益为零。

### 案例 2：`spring.security.user.password` — 保留 @Value

**所在的 StatisticsController.java：**

```java
@Value("${spring.security.user.password}")
private String adminPassword;
```

只在 `StatisticsController` 一个地方使用，用于访问 Actuator 端点时的 Basic Auth 认证。同样满足"Spring 原生 + 单点使用"的条件。

### 案例 3（反例）：`swu.key` — 必须提取

**提取前：**

```
DesEncryptionController   → @Value("${swu.key}")
SWUPasswordLoginStrategy  → @Value("${swu.key}")
SWUCampusScraper          → @Value("${swu.key}")
```

同一个自定义 key 散落在 3 个文件中。修改 key 名时容易遗漏。提取为 `SwuProperties.key()` 后，修改只需改一处。

### 案例 4（反例）：`qcloud.cos.secretId` — 必须提取

**提取前：**

```
CloudConfig    → @Value("${qcloud.cos.secretId}")
UploadService  → @Value("${qcloud.cos.secretId}")
```

两个文件重复注入同一个值，而且还有 `secretKey`、`region`、`bucketName`、`hostname` 等配套属性。提取为 `CosProperties` 后，5 个相关属性聚合成一个对象，构造器注入一个参数解决所有问题。

## 决策流程图

```
@Value 属性
    │
    ├── 命名空间是 spring.* / server.* 等框架前缀？
    │       └── 是 → 保留 @Value（框架自管，不越权）
    │
    ├── 被 ≥ 2 个文件引用？
    │       └── 是 → 提取为 @ConfigurationProperties
    │
    ├── 同一命名空间有 ≥ 3 个 key 散落在不同文件？
    │       └── 是 → 提取为 @ConfigurationProperties（聚合管理）
    │
    └── 只有 1 个文件使用，且 key 数量 ≤ 2？
            └── 是 → 保留 @Value（不值得建类）
```

## 实际结果

| 属性 | 使用文件数 | 决策 | 理由 |
|------|-----------|------|------|
| `swu.key` | 3 | 提取 | 重复注入 |
| `swu.UA` | 3 | 提取 | 重复注入 |
| `swu.jw.*` | 2 | 提取 | 聚合到 `SwuProperties.jw()` |
| `swu.miniapp.*` | 1 | 提取 | 与其他 swu 属性聚合 |
| `qcloud.cos.*` | 2 | 提取 | 重复注入 + 5 个配套属性 |
| `weather.*` | 1 | 提取 | 4 个属性聚合，语义完整 |
| `notification.telegram.*` | 1 | 提取 | 2 个配套属性聚合 |
| `spring.mail.from` | 1 | **保留** | 框架原生 + 单点 |
| `spring.security.user.password` | 1 | **保留** | 框架原生 + 单点 |

## 核心原则

> **"提取"的价值在于消除重复和聚合关联。如果既没有重复，关联属性也只有一个，提取只是把 `@Value` 换了一个写法，没有带来任何收益。"**

换句话说：**框架自带的不碰，自己写的不散。**
