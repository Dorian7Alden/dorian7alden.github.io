## redis-cli 常用命令操作（Web开发版）

### 文档说明
> 本文档面向Web开发人员，整理redis-cli中高频使用的命令，覆盖Redis核心数据结构（字符串、哈希、列表、集合、有序集合），聚焦Web开发场景下的实际应用，便于快速上手Redis命令操作。

### 前置准备
1. 启动redis-cli：打开终端，执行`redis-cli`即可连接本地Redis（默认端口6379）；若连接远程Redis，执行`redis-cli -h <IP地址> -p <端口> -a <密码>`（Web开发中需注意密码安全，避免明文传输）。
2. 测试连接：执行`ping`，返回`PONG`表示连接成功。

---

### 1. 字符串（String）
> Web开发中最常用的数据结构，适用于存储单值数据（如用户token、计数器、缓存简单数据）。

#### 核心命令
| 命令 | 说明 | 示例 |
|------|------|------|
| SET | 设置键值对，支持过期时间（Web场景常用：缓存用户信息、临时token） | `SET user:1001 "{'name':'张三','age':25}" EX 3600`（设置1小时过期） |
| GET | 获取指定键的值 | `GET user:1001` |
| DEL | 删除指定键 | `DEL user:1001` |
| INCR | 数字值自增1（适用于计数器：文章阅读量、接口访问次数） | `INCR article:888:read_count` |
| DECR | 数字值自减1 | `DECR article:888:read_count` |
| SETNX | 仅当键不存在时设置值（分布式锁场景常用） | `SETNX lock:order:10001 "locked" EX 10` |
| MSET | 批量设置键值对 | `MSET user:1002 "李四" user:1003 "王五"` |
| MGET | 批量获取键值对 | `MGET user:1002 user:1003` |

#### 常用场景示例
```bash
# 缓存用户登录token（1小时过期）
SET token:user:1001 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" EX 3600
# 获取token
GET token:user:1001
# 文章阅读量计数
INCR article:888:read_count
# 查看阅读量
GET article:888:read_count
```



### 2. 哈希（Hash）
> 适用于存储结构化数据（如用户信息、商品信息），相比String更节省空间，可单独操作字段，Web开发中高频用于存储对象类数据。

#### 核心命令
| 命令 | 说明 | 示例 |
|------|------|------|
| HSET | 设置哈希表中指定字段的值 | `HSET user:1001 name "张三" age 25 email "zhangsan@example.com"` |
| HGET | 获取哈希表中指定字段的值 | `HGET user:1001 name` |
| HMSET | 批量设置哈希表字段值（Redis 4.0后推荐用HSET替代） | `HMSET user:1002 name "李四" age 26 email "lisi@example.com"` |
| HMGET | 批量获取哈希表字段值 | `HMGET user:1002 name age` |
| HGETALL | 获取哈希表中所有字段和值 | `HGETALL user:1001` |
| HDEL | 删除哈希表中指定字段 | `HDEL user:1001 email` |
| HEXISTS | 判断哈希表中指定字段是否存在 | `HEXISTS user:1001 age` |
| HKEYS | 获取哈希表中所有字段名 | `HKEYS user:1001` |
| HVALS | 获取哈希表中所有字段值 | `HVALS user:1001` |
| HLEN | 获取哈希表中字段的数量 | `HLEN user:1001` |

#### 常用场景示例
```bash
# 存储用户完整信息
HSET user:1001 name "张三" age 25 gender "男" phone "13800138000"
# 获取用户姓名和手机号
HMGET user:1001 name phone
# 更新用户年龄
HSET user:1001 age 26
# 查看用户所有信息
HGETALL user:1001
```



### 3. 列表（List）
> 有序、可重复的字符串集合，适用于实现队列/栈、消息通知、最新列表（如用户消息列表、商品评论列表）。

#### 核心命令
| 命令 | 说明 | 示例 |
|------|------|------|
| LPUSH | 从列表左侧（头部）添加元素 | `LPUSH msg:user:1001 "您的订单已支付"` |
| RPUSH | 从列表右侧（尾部）添加元素 | `RPUSH comment:goods:2001 "商品质量很好"` |
| LPOP | 从列表左侧弹出元素（栈：先进后出） | `LPOP msg:user:1001` |
| RPOP | 从列表右侧弹出元素（队列：先进先出） | `RPOP comment:goods:2001` |
| LRANGE | 获取列表指定范围的元素（Web场景：分页查询评论） | `LRANGE comment:goods:2001 0 9`（获取前10条） |
| LLEN | 获取列表长度 | `LLEN comment:goods:2001` |
| LREM | 删除列表中指定数量的指定元素 | `LREM msg:user:1001 1 "您的订单已支付"`（删除1个该元素） |

#### 常用场景示例
```bash
# 实现用户消息队列（新消息从左侧加入）
LPUSH msg:user:1001 "消息1"
LPUSH msg:user:1001 "消息2"
# 查看用户所有消息（从头部到尾部）
LRANGE msg:user:1001 0 -1
# 消费消息（从尾部弹出，先进先出）
RPOP msg:user:1001
# 分页查询商品评论（第1页，每页10条）
LRANGE comment:goods:2001 0 9
```



### 4. 集合（Set）
> 无序、唯一的字符串集合，适用于存储不重复的数据集（如用户标签、点赞用户列表、抽奖名单）。

#### 核心命令
| 命令 | 说明 | 示例 |
|------|------|------|
| SADD | 向集合中添加元素 | `SADD tag:user:1001 "技术" "美食" "旅行"` |
| SMEMBERS | 获取集合中所有元素 | `SMEMBERS tag:user:1001` |
| SREM | 从集合中删除指定元素 | `SREM tag:user:1001 "美食"` |
| SISMEMBER | 判断元素是否在集合中（Web场景：检查用户是否点赞） | `SISMEMBER like:article:888 1001` |
| SCARD | 获取集合元素数量 | `SCARD tag:user:1001` |
| SINTER | 求多个集合的交集（Web场景：共同好友、共同标签） | `SINTER tag:user:1001 tag:user:1002` |
| SUNION | 求多个集合的并集 | `SUNION tag:user:1001 tag:user:1002` |
| SDIFF | 求多个集合的差集 | `SDIFF tag:user:1001 tag:user:1002` |
| SPOP | 随机弹出集合中的一个元素（抽奖场景） | `SPOP lottery:202401` |

#### 常用场景示例
```bash
# 给用户添加标签
SADD tag:user:1001 "前端开发" "Vue" "React"
# 检查用户是否有某个标签
SISMEMBER tag:user:1001 "Vue"
# 文章点赞（避免重复点赞）
SADD like:article:888 1001 1002 1003
# 查看点赞用户列表
SMEMBERS like:article:888
# 抽奖（随机抽取1名获奖者）
SPOP lottery:202401
```



### 5. 有序集合（Sorted Set/ZSet）
> 有序、唯一的字符串集合，每个元素关联分数（score），按分数排序，适用于排行榜、带权重的队列（如商品销量榜、用户积分排名）。

#### 核心命令
| 命令 | 说明 | 示例 |
|------|------|------|
| ZADD | 向有序集合添加元素（指定分数） | `ZADD rank:goods:sales 100 2001 80 2002 150 2003`（商品ID:2001销量100） |
| ZRANGE | 按分数升序获取指定范围元素（可带分数） | `ZRANGE rank:goods:sales 0 2 WITHSCORES`（获取前3名，带销量） |
| ZREVRANGE | 按分数降序获取指定范围元素（Web场景：排行榜常用） | `ZREVRANGE rank:goods:sales 0 2 WITHSCORES`（销量榜前3名） |
| ZREM | 删除有序集合中指定元素 | `ZREM rank:goods:sales 2002` |
| ZSCORE | 获取元素的分数 | `ZSCORE rank:goods:sales 2001` |
| ZCARD | 获取有序集合元素数量 | `ZCARD rank:goods:sales` |
| ZINCRBY | 给元素的分数增加指定值（Web场景：更新销量、积分） | `ZINCRBY rank:goods:sales 10 2001`（商品2001销量+10） |
| ZRANK | 获取元素的升序排名（从0开始） | `ZRANK rank:goods:sales 2001` |
| ZREVRANK | 获取元素的降序排名（从0开始） | `ZREVRANK rank:goods:sales 2001` |

#### 常用场景示例
```bash
# 初始化商品销量榜
ZADD rank:goods:sales 50 2001 75 2002 90 2003
# 更新商品2001的销量（+5）
ZINCRBY rank:goods:sales 5 2001
# 获取销量榜前2名（降序，带销量）
ZREVRANGE rank:goods:sales 0 1 WITHSCORES
# 查看商品2002的销量排名
ZREVRANK rank:goods:sales 2002
```

---

### 通用命令
> 适用于所有数据结构的基础命令，Web开发中用于管理Redis键、查看状态等。

| 命令 | 说明 | 示例 |
|------|------|------|
| KEYS | 匹配查找键（生产环境慎用，性能差） | `KEYS user:*`（查找所有以user:开头的键） |
| EXISTS | 判断键是否存在 | `EXISTS user:1001` |
| EXPIRE | 给指定键设置过期时间（单位：秒） | `EXPIRE tag:user:1001 86400`（24小时过期） |
| TTL | 查看键的剩余过期时间（-1：永不过期，-2：已过期） | `TTL user:1001` |
| PERSIST | 移除键的过期时间 | `PERSIST user:1001` |
| TYPE | 查看键的数据结构类型 | `TYPE user:1001`（返回hash/string/list等） |
| FLUSHDB | 清空当前数据库（生产环境慎用） | `FLUSHDB` |

#### 常用场景示例
```bash
# 查找所有文章相关的键
KEYS article:*
# 给临时缓存设置10分钟过期
EXPIRE cache:activity:2024 600
# 查看缓存剩余有效期
TTL cache:activity:2024
# 检查键的数据类型
TYPE rank:goods:sales # 返回zset
```

### 注意事项
> 1. 生产环境中避免使用`KEYS *`，推荐用`SCAN`命令（迭代式查找，不阻塞Redis）；
> 2. 设置过期时间时，优先在`SET`/`HSET`等命令中直接指定（如`SET key value EX 3600`），减少多次命令交互；
> 3. Web开发中Redis键名建议遵循统一规范（如`业务:模块:ID:属性`），便于维护；
> 4. 高并发场景下，注意Redis命令的原子性（如`SETNX`实现分布式锁），避免数据不一致。