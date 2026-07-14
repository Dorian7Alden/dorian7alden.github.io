# autoSubmit 重构设计

## 背景

`scripts/autoSubmit/` 是基于 Playwright (Chromium) 的自动化在线评测工具。存在问题：

- 依赖 Playwright（~400MB chromium），启动慢，资源重
- 浏览器实例加锁串行使用，并发受限
- server.js ~600 行，路由、浏览器管理、队列逻辑混杂
- 登录态维护复杂（storageState 持久化、验证码手动输入）

已在 `/home/dorian/Desktop/autoSubmit` 验证了纯 fetch + cheerio 的替代方案：直接用 HTTP cookie 认证，fetch 请求替代页面导航和 DOM 操作，每个脚本既是 CLI 工具也是可引入的模块。

## 目标

用 Desktop 版的纯 fetch 方案替换 Playwright，保留 Web 面板和队列功能。核心原则：

- **server.js 退化为薄路由层**：只做 HTTP → 模块函数转发
- **核心逻辑归入模块**：每个 api 脚本 CLI 和 require 两用
- **API 签名不变**：index.html 不需要改
- **不引入新依赖**：仅保留 cheerio

## 目录结构

```
scripts/autoSubmit/
├── api/                       # 核心脚本（双重模式：CLI + 模块）
│   ├── fetch-problems.js       #   获取题目列表
│   ├── fetch-ranks.js          #   获取排行榜
│   ├── submit.js               #   提交单题测评
│   └── query-status.js         #   轮询等待测评结果
├── config/
│   ├── config.json             #   cookies / userID / 仓库地址
│   └── params.json             #   题目固定参数
├── lib/
│   ├── git.js                  #   git 操作（branches / rev-parse / fetch）
│   └── queue.js                #   提交队列状态机
├── data/                       # 持久化数据
│   ├── status-cache.json
│   ├── rank-cache.json
│   └── submit-history.json
├── server.js                   # 薄 HTTP 路由层
├── index.html                  # Web 面板（不改）
├── package.json
└── README.md
```

依赖方向：`server.js` → `api/` + `lib/queue` → `lib/git.js` + `config/`

## 模块接口

### 两种查询模式

评测平台有两类操作，性质不同：

| 类型 | 场景 | 请求次数 | 耗时 |
|------|------|----------|------|
| **单次查询** | 查看题目列表、排行榜 | 1 次，立即返回 | ~1s |
| **轮询等待** | 提交后等测评结果 | 多次，间隔 5s，最长 30min | 分钟级 |

**单次查询**：fetch → 解析响应 → 返回数据。用在 `/api/status`、`/api/leaderboard`。

**轮询等待**：提交后平台异步评测，需要反复查 `showOJPProcessJSON.jsp`，直到 `ret !== "0"` 表示完成。用在队列提交流程中 `submit()` 之后。

### api/ 脚本

每个文件遵循统一的双重模式：

```js
// CLI: node api/submit.js 3 main
if (require.main === module) { ... }

// 模块引入
const submit = require('./api/submit.js');
const result = await submit(3, 'main');
```

**fetch-problems.js** — `() → problems[]` 【单次查询】
- POST contestindex.jsp，cheerio 解析 HTML
- 一次请求，立即返回

**fetch-ranks.js** — `() → { problems, perf }` 【单次查询】
- POST contest_rank_load.jsp，cheerio 解析 HTML
- 一次请求，立即返回

**submit.js** — `(number, branch?) → { status, body }` 【单次查询】
- 从 config/ 读 cookies 和 params
- POST `application/x-www-form-urlencoded` 到 `showOJPProcessMsg.jsp`
- 一次请求，返回提交确认

**query-status.js** — `(number) → result` 【轮询等待】
- GET `showOJPProcessJSON.jsp`，每 5s 间隔，最长 360 次（30min）
- `result[0].ret === "0"` → 测评中，继续等
- `result[0].ret` 为其他值 → 测评完成，立即返回

### lib/git.js

```js
getBranches()          → string[]
getBranchHead(branch)  → string|null
refreshRepo()          → boolean
```

### lib/queue.js

从 server.js 抽出的队列状态机，不依赖 HTTP / DOM：

```js
const q = createQueue({ onItemDone, onItemFail });
q.add({ problemNum, branch })
q.remove(id)
q.reorder(id, toIndex)
q.start()
```

内部调用 `submit()` → `query-status()`。

### server.js

HTTP 路由层，每个端点的处理为：**解析请求 → 调用模块函数 → 返回 JSON**。

API 端点：

| 端点 | 实现 |
|------|------|
| `/api/status` | fetch-problems（单次查询）+ 缓存 |
| `/api/leaderboard` | fetch-ranks + 缓存 |
| `/api/branches` | git.getBranches() |
| `/api/branch-head` | git.getBranchHead(branch) |
| `/api/refresh-repo` | git.refreshRepo() |
| `/api/submit` | submit(number, branch) |
| `/api/queue` | queue 状态序列化 |
| `/api/queue/add` | q.add() |
| `/api/queue/remove` | q.remove() |
| `/api/queue/reorder` | q.reorder() |
| `/api/queue/start` | q.start() |

## 错误处理

旧版 `lib/errors.js`（ErrorCode 分类）和 `lib/retry.js`（退避重试）是为 Playwright 不确定性设计的。新版采用简单模型：

- 网络错误 → HTTP 502
- 认证过期 → HTTP 401
- 平台异常 → HTTP 502，透传错误信息

## 删除清单

- `lib/shared.js` — Playwright 操作封装
- `lib/errors.js` — 不再需要的错误分类
- `lib/retry.js` — 不再需要的重试策略
- `js/` — 旧的 CLI 脚本目录
- `node_modules/playwright` — 不再需要的浏览器依赖
- `screenshots/` — 不再需要的截图目录
- `docs/platform-analysis.md` — 过时的页面结构分析

## 迁移步骤

### Step 1：搭建新骨架
- 从 Desktop 版复制 api/、config/ 到 scripts/autoSubmit/
- 新建 lib/git.js、lib/queue.js
- 确认 CLI 模式独立运行

### Step 2：重写 server.js
- 用新模块替换 Playwright 调用
- API 端点和响应格式不变
- 启动 Web 面板验证

### Step 3：清理
- 删除旧文件，更新 package.json，更新 README

## 不变项

- index.html 不做修改
- API 端点路径和响应格式不变
- data/ 文件格式不变
