## 2026-04-07 星期二



明天晚上有个蓝桥杯的线上入门赛，可惜有英语课。

![Snipaste_2026-04-07_22-47-48](https://gitee.com/kualk/pic-go/raw/master/imgs/Snipaste_2026-04-07_22-47-48.png)



#### 算法

复杂度要求是 O(nlogn) - O(1) 的话，多半是要递归实现了。

链表排序采用的思想是分治法，跟快排类似。[排序链表](https://leetcode.cn/problems/sort-list/) 具体还没掌握熟悉。明天再看一遍。

[LRU 缓存](https://leetcode.cn/problems/lru-cache/)



### 后端规范 - Spring Boot 项目如何优雅的实现接口参数校验？

中大型项目不用 @Valid 注解，明令禁止。存在以下两个问题：（难以维护、groups 分组也不好用）

- **校验逻辑被拆散到了两个地方**：实体类的定义中，Controller 的参数校验部分
- **多个端调用 ** (pc,app,小程序等) **时静态规则无法灵活适配**：同一个接口往往要同时给 PC 端、APP 端、小程序端、H5 端调用

【最佳实践】封装一个 `ParameterValidator` 链式校验工具，所有校验统一在 Controller 内完成。既能统一在 Controller 内完成所有校验,又能彻底消灭 if 地狱,还能一次性收集所有校验错误:

```java
// 链式参数校验器，支持一次性收集所有校验错误,避免if地狱
public class ParameterValidator {

    private final List<String> errors = new ArrayList<>(); // 用一个 List 类型的 errors 对象一次性返回所有错误

    public static ParameterValidator init() {
        return new ParameterValidator();
    }

    public ParameterValidator notNull(Object value, String message) {
        if (value == null) { errors.add(message); }
        return this; // 返回当前对象，链式调用
    }
    public ParameterValidator notEmpty(Collection<?> collection, String message) {
        if (collection == null || collection.isEmpty()) { errors.add(message); }
        return this; // 返回当前对象，链式调用
    }
	// ......
    // 校验不通过则抛出业务异常
    public void validateAndThrow() {
        if (!errors.isEmpty()) { throw new BusinessException("PARAM_ERROR", String.join("; ", errors)); }
    }
}
```

```java
// 使用示例
@PostMapping("/save")
public Result<Long> save(@RequestBody SaveDeliveryRuleRequest command) {

    ParameterValidator.init() // 链式调用，清晰直观，统一处理
        .hasLength(command.getWarehouseCode(), "仓库编码不能为空")
        .hasLength(command.getWarehouseName(), "仓库名称不能为空")
        .hasLength(command.getWarehouseType(), "仓库类型不能为空")
        .hasLength(command.getMaterialCode(), "物料编码不能为空")
        .notNull(command.getShopId(), "门店ID不能为空")
        .isTrue(!"xxxx".equals(command.getWarehouseType()) 
                || StringUtils.isNotBlank(command.getSupplierCode()),
            "供应商仓库必须指定供应商编码")
        .validateAndThrow();

    return Result.success(deliveryRuleApplicationService.save(command));
}
```

