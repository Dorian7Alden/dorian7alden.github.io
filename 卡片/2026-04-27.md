【Spring MVC】multipart/form-data 与 application/json 的本质区别

---

文件上传请求的 **Content-Type** 为 `multipart/form-data`，请求体是**分段结构**——包含普通字段、文件字段、二进制数据，**不是一个完整的 JSON 字符串**。

而 JSON 接口的 Content-Type 为 `application/json`，请求体是**单一 JSON 字符串**，可直接被 Jackson 反序列化为对象。

> 核心差异：multipart 是**多段混合数据**，JSON 是**单一文本数据**，两者的解析方式完全不同。


【Spring MVC】@ModelAttribute 与 @RequestBody 的适用场景与选择

---

Spring MVC 有两套**参数解析机制**：

| 注解 | 解析机制 | 适用 Content-Type |
|------|----------|------------------|
| `@RequestBody` | JSON 解析 (Jackson) | `application/json` |
| `@ModelAttribute` | 表单绑定 (DataBinder) | `multipart/form-data` |

当请求是 **multipart** 类型时，`@RequestBody` 无法将分段二进制数据解析为 `MultipartFile` 对象，会直接报错。因此只要接口包含 `MultipartFile` 参数，**必须使用** `@ModelAttribute`。

> 本质原因：文件上传走的是**表单绑定机制**，而不是 JSON 解析机制。


【Spring MVC】文件上传的内部处理流程

---

当请求为 `multipart/form-data` 时，Spring 内部处理链路：

1. **MultipartResolver** 拦截并解析请求，拆分出普通字段与文件
2. 通过 **DataBinder** 将字段值绑定到目标对象上
3. 这一整套流程正是 `@ModelAttribute` 的底层工作机制

> 不是 Spring "自动识别"了文件，而是 MultipartResolver 提前做了预处理，再由 DataBinder 完成绑定。


【Spring MVC】consumes 参数的作用与 415 响应机制

---

`consumes` 用于**限制接口只接受特定的 Content-Type**。

- **不写 consumes**：Spring 默认允许多种类型（JSON、form-data、form-urlencoded），但如果客户端用错误的 Content-Type 调用，会在**内部解析阶段报错**，错误信息不直观
- **写了 consumes**：Spring 在进入 Controller **之前**就校验 Content-Type 是否匹配，不匹配直接返回 **415 Unsupported Media Type**

优势：**更早失败**、**更清晰的接口契约**、**更安全**。


【Spring MVC】produces 参数与 HTTP 内容协商机制

---

`produces` 用于**限制接口返回的数据格式**，本质是 HTTP **内容协商机制（Content Negotiation）** 的显式约束。

Spring 根据两个 Header 决定行为：

| Header | 作用 | 对应注解 |
|--------|------|---------|
| `Content-Type` | 告知服务端请求体的格式 | `consumes` |
| `Accept` | 告知服务端客户端期望的返回格式 | `produces` |

若接口声明 `produces = MediaType.APPLICATION_JSON_VALUE`，但客户端请求头 `Accept: text/html`，Spring 会返回 **406 Not Acceptable**。


【后端规范】企业开发中 consumes / produces 的编写规范

---

不同项目阶段对 `consumes` / `produces` 的要求：

| 项目类型 | 是否写 |
|----------|--------|
| 个人项目 | 不强制 |
| 中型项目 | 重要接口建议写 |
| 大厂 / 成熟团队 | **强制写** |

- **文件上传接口**：必须写 `consumes = MediaType.MULTIPART_FORM_DATA_VALUE`
- **JSON 接口**：规范团队会同时写 `consumes = MediaType.APPLICATION_JSON_VALUE` 和 `produces = MediaType.APPLICATION_JSON_VALUE`

> 这是**接口契约设计**的体现，让 API 的输入输出约束显式化、文档化。


【Spring MVC】请求解析完整链路与核心组件

---

Spring MVC 处理一个 HTTP 请求的完整链路：

```
HTTP 请求
    ↓
DispatcherServlet（前端总控）
    ↓
HandlerMapping（查找 Controller）
    ↓
HandlerAdapter（适配并调用）
    ↓
根据 Content-Type 选择解析方式
    ↓
┌──────────────┬────────────────┐
│ JSON         │ multipart/form │
│ @RequestBody │ @ModelAttribute│
└──────────────┴────────────────┘
    ↓
参数绑定
    ↓
进入 Controller 方法
```

> 理解这条链路是从「会用 Spring」进阶到「理解 Spring MVC 内部原理」的关键分水岭。


【Git】新项目第一个开发分支的创建规范

---

为新项目开启第一个开发分支的标准流程：

```bash
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop
```

核心原则：**保护 main 分支**，日常开发在 `develop` 分支上进行，功能稳定后再合并回 `main` 并打 tag。

> main 是「成品仓库」，develop 是「开发集散地」。


【Git】小团队精简 Git Flow 策略

---

对于 1-2 人小团队（或单人项目），推荐**精简版 GitHub Flow**：

- 保留 `main` + `develop` + 短命的 `feat/xxx` 分支
- 大多数时候直接在 `develop` 上开发
- 完成里程碑后合并到 `main` 并**打 tag**
- 去掉 `release` 和 `hotfix` 分支（除非有线上版本需要维护）

> 核心认知：对小项目而言，**tag 比分支更重要**，tag 才是真正的版本记录。


【Git 分支管理】dev / feat / release / hotfix 四种分支的职责与生命周期

---

| 分支 | 生命周期 | 职责 |
|------|---------|------|
| `dev` | **长期存在** | 日常开发集散地，所有功能分支合并到这里 |
| `feat/*` | 临时，完成后**删除** | 单个功能开发，完成后合并回 `dev` |
| `release/*` | 临时，完成后**删除** | 版本发布前的准备（改版本号、文档、测试） |
| `hotfix/*` | 临时，完成后**删除** | 从 `main` 切出，紧急修复线上 bug |

> 核心原则：`release` 和 `hotfix` 都是**临时分支**，用完必须删除。


【Git 分支管理】release 分支的完整合并流程

---

release 分支的正确操作流程（**顺序不可颠倒**）：

1. 从 `dev` 切出 `release/v1.2.0`
2. 在 release 分支上**修改版本号文件**
3. 将 release **合并到 `main`**
4. 在 `main` 上**打 tag**（`git tag v1.2.0`）
5. 将 release **合并回 `dev`**（确保 dev 也获得版本号变更）
6. **删除** release 分支（本地 + 远程）

> 关键点：tag 必须在 merge 到 main **之后**在 main 上打，而不是在 release 分支上打。


【Git 分支管理】hotfix 分支的完整合并流程

---

hotfix 分支的正确操作流程：

1. 从 `main` 切出 `hotfix/v1.2.1`
2. 修复 bug，修改 **patch 版本号**
3. 合并到 `main`
4. 在 `main` 上**打 tag**（`git tag v1.2.1`）
5. **合并回 `dev`**（确保修复同步到开发线）
6. **删除** hotfix 分支

> hotfix 是唯一从 `main` 切出的分支，因为它针对的是线上紧急问题。


【Git】版本号文件与 Git tag 的本质区别

---

| 概念 | 是什么 | 存储位置 |
|------|--------|---------|
| **版本号文件** | 写在代码文件中的版本字段（如 `package.json` 的 `"version": "1.2.0"`） | 代码仓库内 |
| **Git tag** | Git 的标记，附着在某个 commit 上（`git tag v1.2.0`） | Git 数据库中 |

> 版本号文件可被程序运行时读取；tag 用于在 Git 历史中标记发布点。两者需要**严格一致**，但本质是完全不同的东西。


【Git】Git tag 的附着机制——tag 不会随 merge 转移

---

Git tag 是指向**特定 commit** 的静态引用，**不会随分支合并而转移**。

- 在 `release/v1.2.0` 分支上打 tag → tag 附着在该分支的 commit 上
- 将 release 合并到 `main` 后 → main 获得了**相同代码**，但 tag **仍然指向原 commit**，不会自动出现在 main 上
- 正确做法：合并后在 **main 上重新打 tag**

> tag 是指针，不是数据——merge 只合并代码，不动指针。


【Git 分支管理】main 分支的职责边界与操作规范

---

**允许的 4 类操作**：
1. 合并 `release/*` 分支（常规发布）
2. 合并 `hotfix/*` 分支（紧急修复）
3. 打 tag（标记版本）
4. 只读操作（log、diff、tag 列表）

**禁止的操作**：
- 直接 commit / push 新代码
- 合并 `dev` 到 `main`
- 修改已推送的 tag
- 在 main 上解决冲突
- 删除 main 分支

> 远程仓库应配置保护规则：禁止直接 push、禁止 force push。main 是「成品仓库」，只能通过合并改变内容。


【版本管理】语义化版本号规范（Semantic Versioning）

---

语义化版本格式：**v{major}.{minor}.{patch}**

| 版本位 | 升级条件 |
|--------|---------|
| **major** | 不兼容的重大变更（如重构架构、API 破坏性变更） |
| **minor** | 新增功能，向下兼容 |
| **patch** | bug 修复，不影响功能 |

> 例如：`v1.3.2` → major=1, minor=3, patch=2。修复一个 bug → `v1.3.3`；新增一个功能 → `v1.4.0`；架构大改 → `v2.0.0`。


【版本管理】release / hotfix 流程中的版本号更新规范

---

版本号管理的核心原则：

- **版本号只在 release / hotfix 分支上修改**，不在 dev 或 feat 分支上修改
- 文件版本号与 tag 必须**严格一致**
- tag 一旦推送至远程，**不可修改**（只能打新版本递增）

流程要点：
- **release 分支**：修改 minor 或 major 版本号 → 合并到 main → 打 tag → 合并回 dev
- **hotfix 分支**：修改 patch 版本号 → 合并到 main → 打 tag → 合并回 dev

> 合并回 dev 是为了让开发线也获得版本号文件的变更，避免下次 release 时出现版本号冲突。
