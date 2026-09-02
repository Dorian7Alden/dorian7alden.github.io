

[RESTful API 教程 | 菜鸟教程](https://www.runoob.com/restfulapi/restful-api-tutorial.html)



## RESTful API 特点


:::tips
**关键特点：**

+ 无状态：每个请求包含处理所需的所有信息
+ 统一接口：使用标准 HTTP 方法进行操作
+ 资源导向：所有内容都被抽象为资源
+ 可缓存：响应应明确是否缓存

:::



## RESTful API 的核心原则


### 资源与 URI


:::tips
在 REST 中，所有事物都被抽象为资源，每个资源都有唯一的标识符（URI）

:::

<details class="lake-collapse"><summary id="u87d70029"><span class="ne-text">URL</span></summary><p id="u0c39e9bd" class="ne-p"><span class="ne-text">定义：统一资源定位符（Uniform Resource Locator）。</span></p><p id="u38adc26d" class="ne-p"><code class="ne-code"><span class="ne-text">scheme://host[:port#]/path/…/[;url-params][?query-string][#anchor]</span></code></p><p id="uff1502c0" class="ne-p"><span class="ne-text"></span></p><div data-type="tips" class="ne-alert"><p id="u2c1e0f08" class="ne-p"><span class="ne-text">scheme		有我们很熟悉的http、https、ftp以及著名的ed2k，迅雷的thunder等。</span></p><p id="uce9ee0aa" class="ne-p"><span class="ne-text">host   		HTTP服务器的IP地址或者域名</span></p><p id="u2d94f046" class="ne-p"><span class="ne-text">port#  		HTTP服务器的默认端口是80，这种情况下端口号可以省略。如果使用了别的端口，必须指明，例如tomcat的默认端口是8080  </span><a href="http://localhost:8080/" data-href="http://localhost:8080/" target="_blank" class="ne-link"><span class="ne-text">http://localhost:8080/</span></a></p><p id="u6b693806" class="ne-p"><span class="ne-text">path   		访问资源的路径</span></p><p id="ua92758e0" class="ne-p"><span class="ne-text">url-params	所带参数 </span></p><p id="u3e23334b" class="ne-p"><span class="ne-text">query-string	发送给http服务器的数据</span></p><p id="ub3bcf070" class="ne-p"><span class="ne-text">anchor		锚点定位</span></p></div><p id="u7599c88d" class="ne-p"><br></p><p id="u71b14ce2" class="ne-p"><span class="ne-text" style="color: rgb(25, 27, 31)">URL的格式一般由下列三部分组成：</span></p><ol class="ne-ol"><li id="u716f188c" data-lake-index-type="0"><span class="ne-text" style="color: rgb(25, 27, 31)">协议(或称为服务方式);</span></li><li id="uf24f4590" data-lake-index-type="0"><span class="ne-text" style="color: rgb(25, 27, 31)">存有该资源所在的服务器的名称或IP地址(包括端口号);</span></li><li id="u24fc6652" data-lake-index-type="0"><span class="ne-text" style="color: rgb(25, 27, 31)">主机资源的具体地址。</span></li></ol></details>
<details class="lake-collapse"><summary id="u4fb4e2cd"><span class="ne-text">URI</span></summary><p id="ud3437eb2" class="ne-p"><span class="ne-text">定义：统一资源标识符（全称：Uniform Resource Identifier），它是一个字符串用来标示抽象或物理资源。</span></p><p id="u9f634024" class="ne-p"><span class="ne-text"></span></p><p id="u42bb5118" class="ne-p"><span class="ne-text" style="color: rgb(25, 27, 31)">Web上可用的每种资源（ HTML文档、图像、音频、视频片段、程序等）都由一个通用资源标识符（Uniform Resource Identifier, 简称”URI”）进行定位。</span></p><p id="u3f694537" class="ne-p"><span class="ne-text" style="color: rgb(25, 27, 31)"></span></p><p id="u40836c23" class="ne-p"><span class="ne-text" style="color: rgb(25, 27, 31)">URI的格式也由三部分组成：</span></p><ol class="ne-ol"><li id="ube3d13ee" data-lake-index-type="0"><span class="ne-text" style="color: rgb(25, 27, 31)">访问资源的命名机制。</span></li><li id="u39b604dd" data-lake-index-type="0"><span class="ne-text" style="color: rgb(25, 27, 31)">存放资源的主机名。</span></li><li id="u1d709831" data-lake-index-type="0"><span class="ne-text" style="color: rgb(25, 27, 31)">资源自身的名称，由路径表示。</span></li></ol></details>


### HTTP 方法的使用


| <font style="color:rgb(255, 255, 255);">HTTP方法</font> | <font style="color:rgb(255, 255, 255);">描述</font> | <font style="color:rgb(255, 255, 255);">幂等性</font> | <font style="color:rgb(255, 255, 255);">安全性</font> |
| :---: | :---: | :---: | :---: |
| <font style="color:rgb(51, 51, 51);">GET</font> | <font style="color:rgb(51, 51, 51);">获取资源</font> | <font style="color:rgb(51, 51, 51);">是</font> | <font style="color:rgb(51, 51, 51);">是</font> |
| <font style="color:rgb(51, 51, 51);">POST</font> | <font style="color:rgb(51, 51, 51);">创建资源</font> | <font style="color:rgb(51, 51, 51);">否</font> | <font style="color:rgb(51, 51, 51);">否</font> |
| <font style="color:rgb(51, 51, 51);">PUT</font> | <font style="color:rgb(51, 51, 51);">完整更新资源</font> | <font style="color:rgb(51, 51, 51);">是</font> | <font style="color:rgb(51, 51, 51);">否</font> |
| <font style="color:rgb(51, 51, 51);">PATCH</font> | <font style="color:rgb(51, 51, 51);">部分更新资源</font> | <font style="color:rgb(51, 51, 51);">否</font> | <font style="color:rgb(51, 51, 51);">否</font> |
| <font style="color:rgb(51, 51, 51);">DELETE</font> | <font style="color:rgb(51, 51, 51);">删除资源</font> | <font style="color:rgb(51, 51, 51);">是</font> | <font style="color:rgb(51, 51, 51);">否</font> |




### 无状态性


:::tips
每个请求必须包含处理所需的所有信息，服务器不保存客户端状态。这使得API易于扩展和负载均衡。

:::



### 表述形式


:::tips
资源可以有多种表述形式（如JSON、XML），客户端通过Accept头指定需要的格式。

:::



## 示例


### GET 方法


```plain
// 获取所有用户
GET /api/users

// 获取特定用户
GET /api/users/123

// 获取用户的订单
GET /api/users/123/orders
```



### POST 方法


```plain
// 创建新用户
POST /api/users
{
  "name": "张三",
  "email": "zhangsan@example.com"
}

// 创建新订单
POST /api/orders
{
  "userId": 123,
  "items": ["商品A", "商品B"]
}
```



### PUT 方法


```plain
// 更新用户信息
PUT /api/users/123
{
  "name": "李四",
  "email": "lisi@example.com",
  "phone": "13800138000"
}
```



### DELETE 方法


```plain
// 删除用户
DELETE /api/users/123

// 删除订单
DELETE /api/orders/456
```



## HTTP 状态码


| <font style="color:rgb(255, 255, 255);">状态码</font> | <font style="color:rgb(255, 255, 255);">含义</font> | <font style="color:rgb(255, 255, 255);">说明</font> |
| :---: | :---: | :---: |
| <font style="color:rgb(51, 51, 51);">200</font> | <font style="color:rgb(51, 51, 51);">OK</font> | <font style="color:rgb(51, 51, 51);">请求成功</font> |
| <font style="color:rgb(51, 51, 51);">201</font> | <font style="color:rgb(51, 51, 51);">Created</font> | <font style="color:rgb(51, 51, 51);">资源创建成功</font> |
| <font style="color:rgb(51, 51, 51);">400</font> | <font style="color:rgb(51, 51, 51);">Bad Request</font> | <font style="color:rgb(51, 51, 51);">请求有误</font> |
| <font style="color:rgb(51, 51, 51);">401</font> | <font style="color:rgb(51, 51, 51);">Unauthorized</font> | <font style="color:rgb(51, 51, 51);">未授权</font> |
| <font style="color:rgb(51, 51, 51);">404</font> | <font style="color:rgb(51, 51, 51);">Not Found</font> | <font style="color:rgb(51, 51, 51);">资源不存在</font> |
| <font style="color:rgb(51, 51, 51);">500</font> | <font style="color:rgb(51, 51, 51);">Internal Server Error</font> | <font style="color:rgb(51, 51, 51);">服务器内部错误</font> |




## RESTful URL


### URL 设计规范


:::tips
**资源导向的 URL 设计**

RESTful API 的 URL 应该表示"资源"而不是"动作"。 

把 URL 想象成图书馆的书架标签，它告诉你在哪里能找到什么资源。

:::



```plain
GET			/api/users          # 获取所有用户
GET			/api/users/123      # 获取 ID 为 123 的用户
POST		/api/users         	# 创建新用户
PUT 		/api/users/123      # 更新用户 123
DELETE 	/api/users/123   		# 删除用户 123
```

```plain
GET		/api/getUsers       	# 动词出现在 URL 中
POST 	/api/createUser    		# 动作导向而非资源导向
GET 	/api/user/delete/123 	# 混乱的结构
```







### URL 命名规范


:::tips
**使用名词而非动词**

+ ✅ GET /api/books
+ ❌ GET /api/getBooks

:::

:::tips
**使用复数形式**

+ ✅ GET /api/users
+ ❌ GET /api/user

:::

:::tips
**使用小写字母**

+ ✅ GET /api/user-orders
+ ❌ GET /api/UserOrders

:::

:::tips
**使用连字符分隔单词**

+ ✅ GET /api/user-profiles
+ ❌ GET /api/user_profiles
+ ❌ GET /api/userProfiles

:::



### 嵌套资源


```plain
// 获取用户 123 的所有订单
GET /api/users/123/orders

// 获取用户 123 的订单 456
GET /api/users/123/orders/456

// 为用户 123 创建新订单
POST /api/users/123/orders
```



### 查询参数


```plain
javascript// 分页
GET /api/users?page=1&limit=10

// 过滤
GET /api/users?status=active&city=beijing

// 排序
GET /api/users?sort=created_at&order=desc

// 搜索
GET /api/users?search=张三
```



### API 版本控制


```plain
GET /api/v1/users
GET /api/v2/users
```



```plain
GET /api/users
Accept: application/vnd.api+json;version=1
```



## 请求与响应


:::tips
现代 RESTful API 主要使用 JSON（JavaScript Object Notation）格式来传输数据。 

JSON 就像是数据的"通用语言"，简单易读。

:::



### 响应结构设计


```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "张三"
  },
  "message": "操作成功",
  "timestamp": "2024-01-15T08:30:00Z"
}
```



```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入数据验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2024-01-15T08:30:00Z"
}
```



```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "用户1"
    },
    {
      "id": 2,
      "name": "用户2"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 10,
    "totalItems": 100,
    "itemsPerPage": 10
  }
}
```



## 注意强调：


:::tips
当是 GET 请求时，参数可以直接用 params，不用 JSON 传输，速度更快

:::























