## 2026-03-31 星期二



项目经验：

- 写方法实现，一般先写一个 interface ，定义这个类，再开对应的 imlp 文件夹进行实现。类似于 cpp 先写 .h 头文件
- 数据库表有对应的字符编码，数据库的**字符字段**也有对应的编码方式！！！数据库手动建表的时候默认编码是 latin ，字符字段也会是 latin ，尽量不要直接在数据库中设计表以及字段，都靠 SQL 代码执行建表并指定编码方式。
- 写代码先看有没有对应的框架，减少手搓代码。符合规范。开发项目的核心关键词：最佳实践



算法题：

- 观察数据结构：从左往右看，从右往左看，从上往下看，从下往上看。一组一组看，两组两组看。看下标，看元素。
- 做题思路：两个变量，先确定其中一个，遍历另一个。
- 做出来一道栈专题的困难题：[柱状图中最大的矩形](https://leetcode.cn/problems/largest-rectangle-in-histogram/) $O(N^2) - O(N)$ ，最优解：$O(N) - O(N)$ ，需要观察规律，暴力能做就够了



**JavaBean 是什么**？

---

**Bean 是一种特殊的、有规范的、专门用于封装数据的类**。

四个基本规范要求：**类是 public 的**	**私有化属性**	**必须有 public 无参构造方法**	**提供 public 的 getter/setter 方法**

优势：可重用	低耦合	易维护	

> 💡 **注意**: `boolean` *类型的 getter 方法命名是* `isXxx()` *而不是* `getXxx()`
>
> *⚠️* **重点区分：JavaBean 的"属性"由 getter/setter 决定，不是由字段名决定！ ** getXxx() ，xxx 才是属性
>
> Java 是咖啡，Bean 是豆子，咖啡由咖啡豆组成，Java 程序由 JavaBean 组成，合理。
>
> SpringBean 就是 Spring 框架下使用 IoC 容器管理的 Bean 对象。
>
> SpringBean 普遍是单例对象

<img src="https://gitee.com/kualk/pic-go/raw/master/imgs/Bean.png" alt="Bean" style="zoom: 20%;" />



依赖包理清晰：

- MyBatis / JPA / Hibernate ：数据库操作、表与实体映射
- Bean Validation（jakarta.validation）：参数 / 字段校验



工具类需要加载配置参数时，保持静态状态的最佳实践：

1. 使用 @Component 让这个工具类交给 IoC 容器管理
2. 使用 @Value 依赖注入配置的参数
3. 使用 @PostConstruct 设置一个 init 方法，初始化一个静态实例对象，用来后续使用



**Springboot 开发中架构规范的最佳实践**：

---

核心原则：核心原则是 “职责单一、分层解耦、边界清晰、适配业务、不滥用不越界”

小型单体项目：按**技术层**分包	中大型 / 微服务项目：按**业务域**分包（高内聚低耦合，推荐）

标准业务域分包结构示例：（问：不同的业务之间有**交叉**怎么办？）

```plaintext
src/main/java/com/xxx/project
├── common              // 通用组件（全局异常、工具类、常量等）
├── user                // 用户业务域（示例）
│   ├── controller      // 控制层
│   ├── service         // 业务层（接口+实现类）
│   ├── mapper          // 数据访问层（DAO现代落地）
│   ├── entity          // 数据库持久化对象PO
│   ├── dto             // 数据传输对象DTO
│   ├── vo              // 视图对象VO
│   └── bo              // 业务对象BO（复杂业务可选）
├── order               // 订单业务域（结构同上）
└── ProjectApplication.java
```



**Controller 层最佳实践**：

---

**核心职责**：唯一 HTTP 请求入口，只做**参数校验、权限初验、请求转发、结果封装**，绝对不写业务逻辑。

- 入参用 `XXXRequestDTO/XXXQueryDTO` ，出参用 `XXXResponseVO/XXXResponseDTO` ，禁止直接接收 / 返回 PO 对象
- 严格遵循 RESTful 规范
- 参数校验采用 JSR-380 规范（jakarta.validation），基础非法请求直接在 Controller 层拦截
- 统一响应体封装、配合全局异常处理器，Controller 层不写 try-catch
- 配套 SpringDoc/Knife4j 生成接口文档，给 DTO 和接口添加注解，保证文档与代码同步
- 一个 Controller 对应一个业务域，避免单类代码过度膨胀



**Service 层最佳实践**：

---

**核心职责**：唯一承载**业务逻辑**、**事务控制**、**业务规则校验**，是项目的核心层，不直接操作数据库，不处理 HTTP 请求。

- 内部用 BO（业务对象）处理业务逻辑，接收 DTO 转换为 BO/PO，调用 Mapper 层完成数据操作
- 接口与实现分离，方便扩展与单元测试 interface + impl
- 核心业务规则封装到 BO 中，避免沦为纯 set/get 的**贫血模型**
- 禁止循环依赖，A 与 B 相互依赖注入

> (复杂业务)贫血模型场景:Service 层通过大量 get 方法获取到实体类的属性，然后大量的 if 判断。稍有逻辑修改，代码维护很痛苦。
>
> 正确做法：将这种需要结合实体类中的属性判断状态的方法，直接内聚到对应的实体类中，将判断方法写在实体类内部，直接调用。



**Mapper 层最佳实践**：

---

**核心职责**：**仅负责数据库 CRUD 操作，无任何业务逻辑**，是业务逻辑与数据库的唯一隔离层，是传统 DAO 模式的现代落地形式。

- PO（持久化对象），与数据库表一一对应
- 主流使用 MyBatis-Plus 的 `BaseMapper`、Spring Data JPA 的 `JpaRepository`，单表 CRUD 零代码实现
- 严格禁止：Mapper 中编写业务判断逻辑，**多表关联**的业务处理必须上移到 Service 层（Mapper 只**查**、**拼接**数据）
- 多表关联、复杂统计用自定义 XML / 注解 SQL，批量操作用 foreach 标签，避免循环单条插入
- 分页规范：使用 MP 分页插件，避免手写 limit 分页，统一处理分页参数与总数统计
- 安全规范：SQL 占位符必须用`#{}`，禁止用`${}`，防止 SQL 注入



**Model 层最佳实践**：

---

| 对象类型 | 全称         | 核心作用                                               | 流转范围                                   | 最佳实践规范                                                                 | 绝对禁止用法                                                         |
| :------: | :----------: | ------------------------------------------------------ | ------------------------------------------ | -------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| PO       | 持久化对象   | 与数据库表一一对应，唯一承载数据库数据                 | 仅在 Mapper 层、Service 层内部流转         | 1. 字段与数据库表完全映射；<br />2. 仅用 ORM 注解做表映射；<br />3. 纯数据类，无业务逻辑 | 1. 直接返回给前端 / 外部服务；<br />2. Controller 层直接接收；<br />3. 扩展非表字段 |
| DTO      | 数据传输对象 | 跨层 / 跨服务数据传输，隔离内部结构，裁剪字段         | 前后端交互、微服务 RPC 调用、跨服务接口入参出参 | 1. 按场景拆分：入参 RequestDTO、查询 QueryDTO、出参 ResponseDTO；<br />2. 只包含当前场景必要字段；<br />3. 入参加校验注解，出参按需脱敏；<br />4. 微服务间调用必须用 DTO，屏蔽内部 PO 结构 | 1. 一个 DTO 全场景复用；<br />2. 直接映射数据库表；<br />3. 包含业务逻辑；<br />4. 用 PO 替代 DTO |
| BO       | 业务对象     | 封装核心业务数据与业务规则，内聚业务逻辑               | 仅在 Service 层内部流转，不对外暴露         | 1. 组合多个 PO 的数据，承载业务上下文；<br />2. 可封装业务规则方法；<br />3. 复杂业务场景使用，简单 CRUD 可省略 | 1. 对外暴露到 Controller / 前端；<br />2. 直接映射数据库；<br />3. 无业务逻辑的纯字段类 |
| VO       | 视图对象     | 前端视图渲染专用，最终返回给前端的展示对象             | 仅在 Controller 层，作为接口最终返回值      | 1. 严格匹配前端页面字段需求，裁剪敏感字段；<br />2. 包含前端需要的格式化数据；<br />3. 简单项目可与 ResponseDTO 合并 | 1. 传入 Service 层；<br />2. 包含数据库敏感字段                       |



**对象转换的最佳实践**：

---

- 首选：MapStruct 编译期类型安全转换

  - 核心优势：编译期生成转换代码，无反射，性能与手写代码一致，类型安全，编译期报错，支持复杂映射、枚举转换、自定义规则

  - 落地规范：按业务域创建 Convert 接口，**统一管理转换规则**，禁止零散写转换代码

```java
@Mapper(componentModel = "spring")
public interface UserConvert {
    UserConvert INSTANCE = Mappers.getMapper(UserConvert.class);
	// 示例代码
    // PO转响应VO
    UserResponseVO toVO(UserPO userPO);
    // 入参DTO转PO
    UserPO toPO(UserCreateRequestDTO requestDTO);
    // 列表批量转换
    List<UserResponseVO> toVOList(List<UserPO> userPOList);
}
```

- 备选：自定义静态转换方法
  - 适用场景：极简单的 1-2 个字段转换，避免引入框架，代码可读性高。

- 绝对禁止：
  - 禁止使用 `Apache BeanUtils.copyProperties`：性能极差，反射操作，有类型转换坑和安全风险
  - 不推荐大规模使用 `Spring BeanUtils`：运行期反射，字段不匹配无报错，仅适用于极简单场景



后端学习：

- IoC 容器的基本概念
- 使用 xml 配置 SpringBean 的基本用法

