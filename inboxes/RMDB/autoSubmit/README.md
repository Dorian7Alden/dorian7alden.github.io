# educg 自动化脚本

基于 Node.js 的 educg 竞赛平台自动化工具，支持题目列表获取、排行榜拉取、测评提交和结果查询。

## 目录结构

```
├── api/                  # 脚本
│   ├── fetch-problems.js # 获取所有题目列表
│   ├── fetch-ranks.js    # 获取排行榜
│   ├── submit.js         # 提交指定题目测评
│   └── query-status.js   # 查询指定题目测评结果
├── config/               # 配置
│   ├── config.json       # cookies / userID / gitlab 仓库地址
│   └── params.json       # 题目固定参数 (number / assignID / proNum / problemID)
├── data/                 # 输出数据 (problems.json / ranks.json)
├── test/                 # 测试示例
│   ├── test-fetch-problems.js
│   ├── test-fetch-ranks.js
│   ├── test-submit.js
│   └── test-query-status.js
```

## 依赖

```bash
npm install cheerio
```

Node.js v18+（内置 fetch）。

## 用法

### 可执行脚本

```bash
cd api

# 获取题目列表 → ../data/problems.json
node fetch-problems.js

# 获取排行榜 → ../data/ranks.json
node fetch-ranks.js

# 提交题目（number 对应 config/params.json 中的编号 1-11，branch 默认 main）
node submit.js 3
node submit.js 3 main

# 查询测评结果（每 5 秒轮询，最长 30 分钟）
node query-status.js 3
```

### 模块引入

```js
const fetchProblems = require('./api/fetch-problems.js');
const fetchRanks    = require('./api/fetch-ranks.js');
const submit        = require('./api/submit.js');
const pollStatus    = require('./api/query-status.js');

const problems = await fetchProblems();
const ranks    = await fetchRanks();
const result   = await submit(3);              // branch 可选，默认 "main"
const result2  = await submit(3, "feature-x");
const status   = await pollStatus(3);          // 每 5s 轮询，最长 30min
```

## 配置

**config/config.json** — cookies 过期时更新此文件：

- `cookies` — 登录后的 session cookies
- `userID` — 用户标识
- `cgsoucecode` — GitLab 仓库地址

**config/params.json** — 题目固定参数，通常不需要修改。

## 题目分类

- **problems**：10 道常规题目（number 1-10）
- **perf**：1 道性能测试（number 11）

## 查询策略

`query-status.js` 采用轮询方式查询测评结果：

- 每 5 秒请求一次 `showOJPProcessJSON.jsp`
- 响应为 `[{"ret":"1"}, {"content":"..."}]` 数组格式
- `ret: "0"` → 测评中，继续等待
- `ret` 为其他值 → 测评完成，立即返回
- 超过 30 分钟未完成 → 超时退出
