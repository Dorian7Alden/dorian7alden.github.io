`exec()` 是 `BaseValidator` 中提供的一个**链式调用辅助方法**，用于在校验链中执行一段自定义的 `Runnable` 代码块，执行完毕后返回当前校验器实例本身（`this`），从而**不中断链式调用**。

```java
public T exec(Runnable block) {
    block.run();
    return self();
}
```

### 核心作用
- **插入自定义逻辑**：在 `init() → 基础校验 → ... → validateAndThrow()` 这条链中，如果需要在某个位置执行一段**与校验本身无关的操作**（如日志记录、修改 DTO 的临时属性、触发某些副作用等），就可以用 `exec()` 把它嵌进去，而不用单独写一个私有方法。
- **保持链的连续性**：它只是运行代码块，不自动添加校验错误（除非你在代码块里手动调用 `addError`），随后继续返回自身，让后续的校验方法接着调用。

### 使用示例
```java
init()
    .notBlank(dto.getUsername(), "username")
    .exec(() -> log.info("正在校验用户: {}", dto.getUsername()))  // 插入日志
    .hasLength(dto.getUsername(), 3, 20, "username")
    .validateAndThrow();
```

简单来说：`exec()` 是在校验链上开的一个“后门”，允许你安全地执行任意 `Runnable` 而不破坏链式风格。