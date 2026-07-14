# autoSubmit

自动化在线评测工具。基于 HTTP fetch + cheerio，无需浏览器。

## 结构

```
autoSubmit/
├── api/                       # 核心脚本（CLI + 模块两用）
│   ├── fetch-problems.js       #   获取题目列表
│   ├── fetch-ranks.js          #   获取排行榜
│   ├── submit.js               #   提交单题测评
│   └── query-status.js         #   轮询等待测评结果
├── config/
│   ├── config.json             #   cookies / userID / 仓库地址
│   └── params.json             #   题目固定参数
├── lib/
│   ├── git.js                  #   git 操作
│   └── queue.js                #   提交队列
├── data/                       # 持久化数据
├── server.js                   # HTTP 服务（薄路由层）
├── index.html                  # Web 面板
└── package.json
```

## 配置

首次使用需编辑 `config/config.json`，填入登录后的 cookies：

- `cookies`：登录 course.educg.net 后的 session cookies
- `userID`：用户标识
- `cgsoucecode`：GitLab 仓库地址

Cookies 过期时手动更新该文件。

## 快速开始

```bash
# 启动评测面板（浏览器自动打开 http://localhost:3456）
cd scripts/autoSubmit && node server.js
```

## 命令行使用

```bash
cd scripts/autoSubmit

# 获取题目列表
node api/fetch-problems.js

# 获取排行榜
node api/fetch-ranks.js

# 提交单题
node api/submit.js 3 main

# 查询测评结果（轮询等待）
node api/query-status.js 3
```

## 模块引入

```js
const fetchProblems = require('./api/fetch-problems.js');
const fetchRanks    = require('./api/fetch-ranks.js');
const submit        = require('./api/submit.js');
const queryStatus   = require('./api/query-status.js');
```

## HTTP API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/status?refresh=1` | GET | 题目状态（得分/分支/时间） |
| `/api/leaderboard?refresh=1` | GET | 排行榜 |
| `/api/branches` | GET | 远端分支列表 |
| `/api/branch-head?branch=NAME` | GET | 分支最新 commit |
| `/api/refresh-repo` | POST | git fetch --prune |
| `/api/submit` | POST | 提交单题 `{problemNum, branch}` |
| `/api/queue` | GET | 队列状态 |
| `/api/queue/add` | POST | 添加 `{items: [...]}` |
| `/api/queue/remove` | POST | 移除 `{id}` |
| `/api/queue/reorder` | POST | 排序 `{id, toIndex}` |
| `/api/queue/start` | POST | 启动队列 |

## 题目编号

| 编号 | 题目 | 满分 |
|------|------|------|
| 1 | 存储管理 | 5 |
| 2 | 查询执行 | 5 |
| 3 | 唯一索引 | 10 |
| 4 | 查询优化与执行 | 10 |
| 5 | 聚合函数与分组统计 | 10 |
| 6 | Union 集合算子 | 10 |
| 7 | 嵌套循环连接及其优化 | 15 |
| 8 | 事务控制语句 | 5 |
| 9 | 可配置的快照隔离与可串行化隔离级别 | 20 |
| 10 | 基于静态检查点的故障恢复 | 10 |
| 11 | 性能测试 | 100 |
