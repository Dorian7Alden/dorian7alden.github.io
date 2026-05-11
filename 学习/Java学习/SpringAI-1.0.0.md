> 推荐学习的开源项目（提示词管理、重试、批处理、解析提示词、提示词注入）：https://gitee.com/SnailClimb/interview-guide
>
> 中小型项目。没有复杂的 AI 工作流。适合刚入门学习。需要一定的基础。
>
> B 站上的教程，**大多**很基础。对开发 AI 应用没有指导价值。



## SpringAI 框架学习



> 该框架还在更新迭代中，功能还不稳定。1.x 有稳定版本，但是功能不全，2.x 功能更多，但是不稳定。
> 中途被版本冲突搞崩溃了。直接使用 1.x 就好了，没有的功能就自己实现。
> AI 的工作流相关机制，我没了解到有什么好的框架，有一个 LangChain4j 框架，没了解。还得是 Python 。大不了手搓。



### 前置内容



### 提示词存储



核心目标是**避免硬编码**、**提升可维护性**、**支持动态更新**并**确保生产环境稳定性**。

最佳实践：通过资源文件存储。简单易用、与代码分离、支持版本控制、无需额外依赖。

数据库存储，编辑、调整提示词的时候不方便



在 `src/main/resources` 下创建 `prompts` 目录，存放 `.st`（StringTemplate）

```
src/main/resources/
└── prompts/
    ├── xxx-system.st    # 系统提示词
    ├── xxx-user.st   	 # 用户提示词
    └── xxx.st     
```

![image-20260406224329213](https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260406224329213.png)

踩坑：

- 占位符默认是 “{}” ，当提示词中有 JSON 格式的内容时，解析报错！要给 JSON 内容转义。其他内容影响加载时，也都要手动转义！

  ```
  【任务】
  
  提取有效数据
  
  【待解析内容】
  
  {rawContent}
  
  【格式】
  
  严格按如下格式输出：
  \{
  	"name": "string",
  	"age": "number"
  \}
  ```



### 提示词加载

单例，只加载一次。在代码中通过 `@Value` 注入并使用

```java
@Service
public class AnswerEvaluationService {
    // 示例
    private final PromptTemplate systemPT;
    private final PromptTemplate userPT;
    // 构造函数注入
    public AnswerEvaluationService(
            @Value("classpath:prompts/interview-evaluation-system.st") Resource systemPromptResource,
            @Value("classpath:prompts/interview-evaluation-user.st") Resource userPromptResource) {
        this.systemPromptTemplate = new PromptTemplate(systemPT.getContentAsString(StandardCharsets.UTF_8));
        this.userPromptTemplate = new PromptTemplate(userPT.getContentAsString(StandardCharsets.UTF_8));
	}
}
```



### 提示词拼接



#### 插入变量



调用 PromptTemplate 对象的 render 方法，映射占位符以及变量

```java
private final ChatClient chatClient;
private final PromptTemplate sysPrompt;
private final PromptTemplate userPrompt;

@PostMapping("/review")
public Result<ReviewDTO> review(@RequestBody Map<String, String> req) {
	// 这里不应该叫 DTO
    return Result.success(AiChatUtils.chat( // AiChatUtils => 自己封装的方法
            chatClient,
            new Prompt(List.of(
                    new SystemMessage(sysPrompt.render()), 
                    new UserMessage(userPrompt.render(Map.of( // 提示词模板插入变量
                            "originProblem", req.get("problem"),
                            "submission", req.get("submissionContent")))
                    )
            )),
            new BeanOutputConverter<>(ReviewDTO.class)));
}
```



#### 消息列表构建

参考 Prompt 对象的构造函数，通过手动管理 Prompt 对象，可以实现**上下文**机制。

```java
 new Prompt(List.of(
        new SystemMessage(sysPrompt.render()), 
        new UserMessage(userPrompt.render(Map.of( // 提示词模板插入变量
                "originProblem", req.get("problem"),
                "submission", req.get("submissionContent")))
        )
))
```



### 提示词解析

使用 BeanOutputConverter 对象传入实体类的类字面量，**自动**将响应结果封装到对应的实体类中

```java
public class AiChatUtils {
    /**
     * 通用 ai 聊天方法
     *
     * @param chatClient ai 客户端
     * @param prompt     提示词
     * @param converter  结果转换器
     * @return 解析后的实体
     */
    public static <T> T chat(ChatClient chatClient,
                      Prompt prompt,
                      StructuredOutputConverter<T> converter) {
        return chatClient
                .prompt(prompt)
                .call() // .entity() 就是启动自动解析的入口，传入对应的 converter ，转换过程框架都写好了
                .entity(converter); // 使用的时候传入 ==> new BeanOutputConverter<>(ReviewDTO.class)
    }
}
```



存储响应结果的实体类，使用 **`record`** 类型。示例：

```java
/**
 * 评审记录主类
 */
public record ReviewDTO(
        BasicInfo basicInfo,
        List<DimensionDetail> dimensionDetails,
        Double weightedTotalScore
) {

    /**
     * 基本信息
     */
    public record BasicInfo(
            String modelingProblemTitle,
            String scoringDate,
            Integer maxScore
    ) {}

    /**
     * 维度详情
     */
    public record DimensionDetail(
            Integer dimensionIndex,
            String dimensionName,
            Double weight,
            Integer dimensionScore,
            String scoringReason
    ) {}
}
```



### 工作流



核心机制：生产者消费者 + 异步任务 + 线程池 + 批处理 + 结果校验 + 自动重试



#### 生产者消费者设计模式

Producer + Consumer



#### 异步任务

|     特性     |       `@Async`       |  `CompletableFuture`   |   最佳组合（推荐）   |
| :----------: | :------------------: | :--------------------: | :------------------: |
|   实现方式   | 声明式注解（Spring） |  编程式（Java 原生）   |     注解+编程式      |
|  线程池管理  |       自动管理       |        手动管理        |   Spring 自动管理    |
| 任务编排能力 |    无（仅单任务）    | 极强（并行/串行/回调） |         极强         |
|  代码复杂度  |         极低         |          中等          |          低          |
| 企业常用场景 |     简单异步任务     |      复杂任务编排      | 绝大多数异步业务场景 |



#### 线程池

需要手动设置，不能用自带的。



#### 批处理、结果校验、自动重试

暂时没理解



### 复杂的 Agent 范式

> 推荐先用 python 实现，再迁移至 Java
>
> 教程：https://github.com/datawhalechina/hello-agents

ReAct、Plan-and-Solve、Reflection …



### Prompt 

> The Prompt class represents a prompt used in AI model requests. A prompt consists of **one or more messages** and **additional chat options**.

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260405162038219.png" alt="image-20260405162038219" style="zoom:50%;" />

最终大模型发送的是 Prompt 类型的数据，这个 Prompt 可以有 1 条或多条 Message，就是一个消息列表，并且可以携带一下聊天的参数选项。

作用：通过维护 Prompt 可以用来管理上下文



### MessageType

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/image-20260405163237337.png" alt="image-20260405163237337" style="zoom:67%;" />

MessageType 共有 4 个类型，分别是：

- user
- assistant
- system
- tool





