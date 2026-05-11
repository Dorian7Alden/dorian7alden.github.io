# JavaEE 企业级开发规范 —— Controller、Validator、统一响应

## 1. 概述
本文档规定控制层（Controller）、参数校验层（Validator）及统一响应结构（Result）的职责边界与编码规范，确保各层职责单一、逻辑清晰。
适用范围：Spring Boot / Spring MVC 等 JavaEE 企业级后端项目。

## 2. Controller 层规范
### 2.1 核心职责
Controller 仅作为请求入口与响应出口，不承载业务逻辑。职责顺序如下：

1. **接收 DTO**
   - 普通 JSON 请求：使用 `@RequestBody` 绑定 DTO（*禁止使用 `@Valid` 或 `@Validated`*）。
   - 文件与 JSON 混合请求：**统一封装为一个 DTO**，包含 JSON 字段与文件字段（`MultipartFile`）。Controller 通过 `@RequestPart` 分别接收 JSON 部分和文件部分，然后组合到该 DTO 实例中。
   - 条件查询等非必填参数：同样绑定一个 DTO，大部分字段为可空，由 Validator 按需校验。

2. **调用 Validator 完成校验**
调用对应接口的校验器，对 DTO 进行**一次性整体校验**，校验不通过直接抛出参数异常，由全局异常处理器接管。

3. **调用 Service 执行功能**
只做委托，不参与业务编排。

4. **按需组装 VO**
将 Service 返回的业务对象转换为 VO。每个 VO 提供静态工厂方法 `createVO(Entity)`，通过该方法逐字段显式赋值并返回 VO 实例。Controller 只需调用 `xxVO.createVO(entity)`，即可完成安全转换。

5. **返回统一 Result**
返回值类型固定为 `Result`。

### 2.2 典型场景与代码示例
#### 场景一：纯 JSON 请求
```java
@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;
    private final UserCreateValidator userCreateValidator;

    public UserController(UserService userService, UserCreateValidator userCreateValidator) {
        this.userService = userService;
        this.userCreateValidator = userCreateValidator;
    }

    @PostMapping
    public Result<Void> createUser(@RequestBody UserCreateDTO dto) {
        userCreateValidator.validate(dto);
        userService.createUser(dto);
        return Result.success();
    }
}
```

#### 场景二：文件 + JSON 混合请求（统一 DTO）
```java
// DTO 定义（包含文件字段）
public class UserAttachmentDTO {
    private String title;
    private MultipartFile file;
    // getter/setter
}

@RestController
public class AttachmentController {

    private final UserAttachmentValidator userAttachmentValidator;
    private final AttachmentService attachmentService;

    @PostMapping("/upload")
    public Result<String> uploadFile(
            @RequestPart("meta") UserAttachmentDTO meta,
            @RequestPart("file") MultipartFile file) {

        meta.setFile(file);                     // 统一封装到一个 DTO
        userAttachmentValidator.validate(meta);
        String url = attachmentService.save(meta);
        return Result.success(url);
    }
}
```

#### 场景三：条件查询 + VO 转换
```java
@GetMapping("/search")
public Result<List<UserVO>> search(UserQueryDTO dto) {
    userQueryValidator.validate(dto);
    List<User> users = userService.query(dto);

    List<UserVO> voList = new ArrayList<>();
    for (User user : users) {
        UserVO vo = UserVO.createVO(user);      // 调用 createVO 完成逐字段转换
        voList.add(vo);
    }
    return Result.success(voList);
}
```

### 2.3 强制规定
- **禁止**使用 `@Valid`、`@Validated`、`@NotNull` 等任何注解驱动的校验。
- **禁止** Controller 中出现 `try-catch` 处理业务异常（异常处理遵循项目已有规范）。
- **禁止**使用 `BeanUtils.copyProperties` 或类似工具进行 VO 转换，必须通过 `createVO()` 方法逐字段显式赋值。
- VO 必须提供静态工厂方法 `createVO(Entity)`，在方法内完成转换，不可在 Controller 中直接 `set`。

---

## 3. VO 转换规范
### 3.1 CreateVO 静态工厂方法定义
所有 VO 类必须提供静态工厂方法 `createVO`，接收对应的领域对象并返回 VO 实例。

### 3.2 VO 实现示例
```java
public class UserVO {
    private Long id;
    private String username;
    private String email;

    // 不暴露 password 等敏感字段

    public static UserVO createVO(User user) {
        UserVO vo = new UserVO();
        vo.setId(user.getId());
        vo.setUsername(user.getUsername());
        vo.setEmail(user.getEmail());
        // 故意不设置 password、手机号等字段，按需暴露
        return vo;
    }

    // getter/setter ...
}
```

**使用方式**（在 Controller 中）：
```java
User user = userService.getById(id);
UserVO vo = UserVO.createVO(user);
return Result.success(vo);
```

### 3.3 禁止事项
- 严禁在 VO 转换中使用 `BeanUtils.copyProperties` 等反射工具。
- 严禁在 VO 类中直接返回 `Result` 或其他响应结构。
- VO 中不可包含业务逻辑，仅作为数据的视图容器。

---

## 4. Validator 层规范
### 4.1 设计原则
- **唯一校验入口**：所有校验经由 Validator，不依赖注解。
- **一次校验、全量报错**：收集全部错误后统一抛出。
- **完整链式调用**：校验从 `init()` 开始，依次调用基础方法与自定义方法，最后以 `validateAndThrow()` 收尾，形成一条完整的链。
- **自定义校验方法化**：复杂校验逻辑封装为当前 Validator 的私有方法，返回 `this`，无缝融入链式。
- **按业务模块分包**：`validator.user`、`validator.order`、`validator.attachment` 等，每个包对应一个业务模块，**绝不按参数类型（如 `json`、`file`）分包**。包名必须体现业务含义。

### 4.2 包结构示例
```
com.xxx.validator
├── base
│   └── BaseValidator.java
├── user          # 用户模块
│   ├── UserCreateValidator.java
│   ├── UserUpdateValidator.java
│   └── UserQueryValidator.java
├── order         # 订单模块
│   └── OrderSubmitValidator.java
└── attachment    # 附件管理业务模块
    └── UserAttachmentValidator.java
```

> 说明：包名 `attachment` 指代附件管理业务模块，而非因为入参包含文件类型才独立分包。即使是纯 JSON 入参，若属于附件业务，也应置于此包。

### 4.3 基础校验器（BaseValidator）
每个校验方法返回 `this`，内部维护错误列表。子类通过泛型获取自身类型，保证链式调用流畅。错误信息统一使用中文描述，直接作为前端展示给用户的提示。

```java
public abstract class BaseValidator<T extends BaseValidator<T>> {

    protected List<FieldError> errors = new ArrayList<>();

    @SuppressWarnings("unchecked")
    protected T self() {
        return (T) this;
    }

    // 初始化方法，开启链式调用
    public T init() {
        return self();
    }

    // 通用字段校验
    public T notNull(Object value, String errorMessage) {
        if (value == null) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    public T notBlank(String value, String errorMessage) {
        if (value == null || value.trim().isEmpty()) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    public T hasLength(String value, int min, int max, String errorMessage) {
        if (value != null && (value.length() < min || value.length() > max)) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    public T isTrue(Boolean condition, String errorMessage) {
        if (condition != null && !condition) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    public T maxLength(String value, int max, String errorMessage) {
        if (value != null && value.length() > max) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    public T minValue(Integer value, int min, String errorMessage) {
        if (value != null && value < min) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    // 文件校验
    public T fileNotEmpty(MultipartFile file, String errorMessage) {
        if (file == null || file.isEmpty()) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    public T fileMaxSize(MultipartFile file, long maxBytes, String errorMessage) {
        if (file != null && file.getSize() > maxBytes) {
            errors.add(new FieldError(null, errorMessage));
        }
        return self();
    }

    // 自定义帮助方法
    public T addError(String errorMessage) {
        errors.add(new FieldError(null, errorMessage));
        return self();
    }

    public T exec(Runnable block) {
        block.run();
        return self();
    }

    /** 终止校验：存在错误则抛出 ValidationException */
    public void validateAndThrow() {
        if (!errors.isEmpty()) {
            throw new ValidationException(new ArrayList<>(errors));
        }
    }
}
```

### 4.4 具体校验器实现（完整链式 + 自定义方法）
#### 用户创建校验器
```java
@Component
public class UserCreateValidator extends BaseValidator<UserCreateValidator> {

    public void validate(UserCreateDTO dto) {
        // 链式调用：初始化 → 基础校验 → 自定义方法 → 终止
        init()
            .notBlank(dto.getUsername(), "请输入用户名")
            .hasLength(dto.getUsername(), 3, 20, "用户名长度需在3到20个字符之间")
            .notBlank(dto.getPassword(), "请输入密码")
            .passwordComplexity(dto.getPassword())   // 自定义校验方法融入链式
            .validateAndThrow();
    }

    // 自定义校验方法封装为私有方法，返回 this
    private UserCreateValidator passwordComplexity(String password) {
        if (password != null && (password.length() < 6 || !password.matches(".*[A-Z].*"))) {
            addError("密码需至少6位且包含大写字母");
        }
        return self();
    }
}
```

#### 附件业务校验器
```java
@Component
public class UserAttachmentValidator extends BaseValidator<UserAttachmentValidator> {

    public void validate(UserAttachmentDTO dto) {
        init()
            .notBlank(dto.getTitle(), "请输入附件标题")
            .fileNotEmpty(dto.getFile(), "请选择要上传的附件")
            .fileMaxSize(dto.getFile(), 5 * 1024 * 1024, "附件大小不能超过5MB")
            .validateAndThrow();
    }
}
```

#### 条件查询校验器（可选字段）
```java
@Component
public class UserQueryValidator extends BaseValidator<UserQueryValidator> {

    public void validate(UserQueryDTO dto) {
        init()
            .validateAgeRange(dto.getAgeMin(), dto.getAgeMax())
            .validateStatus(dto.getStatus())
            .validateAndThrow();                     // 即使全部可选，也必须有此收尾
    }

    private UserQueryValidator validateAgeRange(Integer ageMin, Integer ageMax) {
        if (ageMin != null && ageMax != null && ageMin > ageMax) {
            addError("最小年龄不能大于最大年龄");
        }
        return self();
    }

    private UserQueryValidator validateStatus(Integer status) {
        if (status != null && !Arrays.asList(0, 1, 2).contains(status)) {
            addError("状态值无效");
        }
        return self();
    }
}
```

### 4.5 异常与错误载体
- `ValidationException` 继承 `RuntimeException`，包含 `List<FieldError>`。
- `FieldError` 包含 `field`（可设为 null）与 `message`（中文提示信息）字段。

---

## 5. 统一响应结构（Result）
| 字段    | 类型   | 说明                                                 |
| ------- | ------ | ---------------------------------------------------- |
| code    | int    | 业务状态码，具体编码及含义严格遵守《业务状态码规范》 |
| message | String | 提示信息                                             |
| data    | T      | 业务数据（包括参数校验错误列表）                     |

`Result` 通过静态工厂方法构建，成功码引用统一常量。

```java
public class Result<T> {
    private int code;
    private String message;
    private T data;

    private Result() {}

    public static <T> Result<T> success() {
        return success(null);
    }

    public static <T> Result<T> success(T data) {
        Result<T> r = new Result<>();
        r.code = StatusCode.SUCCESS;  // 取自《业务状态码规范》
        r.message = "ok";
        r.data = data;
        return r;
    }

    public static <T> Result<T> fail(int code, String message, T data) {
        Result<T> r = new Result<>();
        r.code = code;
        r.message = message;
        r.data = data;
        return r;
    }
}
```

校验失败时，全局异常处理器将 `List<FieldError>` 置入 `data`，具体错误码遵循状态码规范。

---

## 6. 异常处理说明
本规范不重复定义异常处理机制。Validator 抛出的 `ValidationException` 及 Service 层各类异常，由项目已制定的《全局异常处理规范》统一处理为 `Result` 响应。Controller 层严禁捕获异常。

---

## 7. Service 层规范（引用）
- Service 只返回领域对象，不包含视图信息。
- 视图转换全部交由 Controller 侧通过 `createVO()` 完成。

---

## 8. 完整调用流程
```
Client 请求 (JSON / 文件+JSON)
      │
      ▼
Controller 组装 DTO（JSON 部分 + 文件部分统一封装）
      │
      ▼
Validator 链式校验
      │  init() → 基础校验 → 自定义方法 → ... → validateAndThrow()
      │
      ├── 存在错误 → throw ValidationException → 全局异常处理器 → Result(code, message, List<FieldError>)
      │
      └── 校验通过 → Service 执行业务 → 返回领域对象
                              │
                              ▼
                      Controller: xxVO.createVO(entity)
                              │
                              ▼
                       Result.success(vo)
```

---

## 9. 附加约定
- Validator 类名以 `Validator` 结尾，使用 `@Component` 注册，方法统一命名 `validate(DTO)`。
- 链式末尾必须调用 `validateAndThrow()`，禁止在链外单独处理错误。
- 即使接口暂无校验规则，也要保留 Validator 并调用 `validateAndThrow()` 以预留扩展点。
- 文件参数统一作为 DTO 的一个字段，传输时通过多个 `@RequestPart` 组合拼装，不将 `MultipartFile` 作为独立参数传递到 Service。
- DTO 内部严禁使用任何校验注解，校验逻辑全部集中在 Validator 中。
- VO 必须提供静态工厂方法 `createVO(Entity)`，转换时逐字段显式赋值，不得使用任何自动化拷贝工具。
- 业务状态码统一定义、全局异常处理的具体实现请参照项目已有相关规范。