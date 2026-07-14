# autoSubmit 重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用纯 HTTP fetch + cheerio 替代 Playwright，将 server.js 退化为薄路由层，核心逻辑归入独立模块。

**Architecture:** 三层：`api/`（数据获取，CLI/模块两用） → `lib/`（git 操作 + 队列状态机） → `server.js`（HTTP 路由转发）。API 端点和响应格式不变，index.html 不改。

**Tech Stack:** Node.js v18+ (内置 fetch)、cheerio (HTML 解析)、原生 http 模块

## 字段映射速查

Desktop api 脚本输出的字段名 vs index.html 期望的字段名：

| Desktop api 输出 | index.html 期望 | 说明 |
|------------------|----------------|------|
| `number` | `num` | 题目编号 |
| `title` | `name` | 题目名称 |
| `obtainedScore` | `score` | 得分 |
| `maxScore` | `maxScore` | 满分（不变） |
| `lastSubmitTime` | `lastSubmitTime` | 最后提交时间（不变） |
| `testResult` | `feedback` | 批阅信息 |
| *(无)* | `branch` | 需额外 fetch |
| *(无)* | `commitHash` | 由 lib/git.js 提供 |

## Global Constraints

- 仅依赖 cheerio，删除 playwright
- API 端点路径和响应格式不变
- index.html 不做修改
- data/ 文件格式不变

---

### Task 1: 从 Desktop 复制 api/ 和 config/

**Files:**
- Create: `scripts/autoSubmit/api/fetch-problems.js`
- Create: `scripts/autoSubmit/api/fetch-ranks.js`
- Create: `scripts/autoSubmit/api/submit.js`
- Create: `scripts/autoSubmit/api/query-status.js`
- Create: `scripts/autoSubmit/config/config.json`
- Create: `scripts/autoSubmit/config/params.json`

**Interfaces:**
- Produces:
  - `fetchProblems()` → `[{ number, title, maxScore, obtainedScore, lastSubmitTime, testResult, reviewInfo, compileDetail }]`
  - `fetchRanks()` → `{ problems: { columns, ranks }, perf: { columns, ranks } }`
  - `submit(number, branch?)` → `{ status, body }`
  - `queryStatus(number)` → 轮询直到测评完成，返回 `{ number, title, result }`

- [ ] **Step 1: 复制 api/ 脚本**

```bash
cp /home/dorian/Desktop/autoSubmit/api/fetch-problems.js scripts/autoSubmit/api/
cp /home/dorian/Desktop/autoSubmit/api/fetch-ranks.js scripts/autoSubmit/api/
cp /home/dorian/Desktop/autoSubmit/api/submit.js scripts/autoSubmit/api/
cp /home/dorian/Desktop/autoSubmit/api/query-status.js scripts/autoSubmit/api/
```

- [ ] **Step 2: 复制 config/ 文件**

```bash
cp /home/dorian/Desktop/autoSubmit/config/config.json scripts/autoSubmit/config/
cp /home/dorian/Desktop/autoSubmit/config/params.json scripts/autoSubmit/config/
```

- [ ] **Step 3: 安装 cheerio 依赖**

```bash
cd scripts/autoSubmit && npm install cheerio
```

- [ ] **Step 4: 验证 CLI 模式**

```bash
cd scripts/autoSubmit && timeout 10 node api/fetch-problems.js
```

Expected: 输出 problems 到 `data/problems.json`，无报错

```bash
cd scripts/autoSubmit && node api/fetch-ranks.js
```

Expected: 输出 ranks 到 `data/ranks.json`，无报错

- [ ] **Step 5: Commit**

```bash
git add scripts/autoSubmit/api/ scripts/autoSubmit/config/ scripts/autoSubmit/package.json scripts/autoSubmit/package-lock.json
git commit -m "feat(autoSubmit): 添加纯 fetch 版 api 脚本和 config"
```

---

### Task 2: 创建 lib/git.js

**Files:**
- Create: `scripts/autoSubmit/lib/git.js`

**Interfaces:**
- Produces:
  - `getBranches()` → `string[]`
  - `getBranchHead(branch)` → `string | null`
  - `refreshRepo()` → `boolean`

- [ ] **Step 1: 创建 lib/git.js**

```js
'use strict';

const { execSync } = require('child_process');
const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '../../..');

function getBranches() {
  try {
    const out = execSync('git branch -a', { cwd: PROJECT_ROOT, encoding: 'utf8' });
    return out.split('\n')
      .map(l => l.replace(/^\*?\s*/, '').replace(/^remotes\/origin\//, '').trim())
      .filter(b => b && b !== 'HEAD' && !b.includes('->'))
      .filter((b, i, arr) => arr.indexOf(b) === i)
      .sort();
  } catch {
    return [];
  }
}

function getBranchHead(branch) {
  try {
    const hash = execSync(`git rev-parse origin/${branch}`, {
      cwd: PROJECT_ROOT, encoding: 'utf8', timeout: 5000,
    }).trim();
    return hash || null;
  } catch {
    return null;
  }
}

function refreshRepo() {
  try {
    execSync('git fetch origin --prune', { cwd: PROJECT_ROOT, encoding: 'utf8', timeout: 30000 });
    return true;
  } catch {
    return false;
  }
}

module.exports = { getBranches, getBranchHead, refreshRepo };
```

- [ ] **Step 2: 验证 git 函数**

```bash
cd scripts/autoSubmit && node -e "const { getBranches, getBranchHead } = require('./lib/git'); console.log('branches:', getBranches().length); console.log('main head:', getBranchHead('main')?.substring(0, 8));"
```

Expected: 输出 branches 数量和 main 分支的 commit hash 前 8 位

- [ ] **Step 3: Commit**

```bash
git add scripts/autoSubmit/lib/git.js
git commit -m "feat(autoSubmit): 添加 lib/git.js（分支列表/hash/fetch）"
```

---

### Task 3: 创建 lib/queue.js

**Files:**
- Create: `scripts/autoSubmit/lib/queue.js`

**Interfaces:**
- Consumes: `submit(number, branch)` from api/submit.js, `queryStatus(number)` from api/query-status.js, `getBranchHead(branch)` from lib/git.js
- Produces: `createQueue({ onItemDone, onItemFail })` → queue 对象，提供 `add/remove/reorder/start` 方法和 `running/current/items` 属性

- [ ] **Step 1: 创建 lib/queue.js**

```js
'use strict';

const submit = require('../api/submit');
const queryStatus = require('../api/query-status');
const { getBranchHead } = require('./git');

function createQueue({ onItemDone, onItemFail }) {
  let nextId = 1;
  let running = false;
  let current = null;
  let items = [];

  async function processQueue() {
    if (running) return;
    if (items.length === 0) return;
    running = true;

    while (items.length > 0) {
      const item = items[0];
      item.status = 'running';
      item.startTime = new Date().toISOString();
      current = item;

      try {
        console.log(`[队列] 提交题目${item.problemNum} 分支: ${item.branch}`);
        const submitResult = await submit(item.problemNum, item.branch);
        const submitTime = new Date().toISOString();

        console.log(`[队列] 等待题目${item.problemNum} 评测结果...`);
        const pollResult = await queryStatus(item.problemNum);

        item.status = 'done';
        item.result = {
          id: item.id,
          problemNum: item.problemNum,
          branch: item.branch,
          commitHash: item.commitHash,
          submitTime,
          score: pollResult?.result?.[1]?.content || null,
          status: 'done',
        };
        if (onItemDone) await onItemDone(item);
      } catch (err) {
        console.error(`[队列] 题目${item.problemNum} 失败:`, err.message);
        item.status = 'failed';
        item.result = {
          id: item.id,
          problemNum: item.problemNum,
          branch: item.branch,
          commitHash: item.commitHash,
          submitTime: new Date().toISOString(),
          error: err.message,
          status: 'error',
        };
        if (onItemFail) await onItemFail(item, err);
      } finally {
        items.shift();
        current = null;
      }
    }
    running = false;
  }

  return {
    get running() { return running; },
    get current() { return current; },
    get items() { return items; },

    add(entries) {
      const added = [];
      for (const { problemNum, branch } of entries) {
        const commitHash = getBranchHead(branch);
        const item = { id: nextId++, problemNum, branch, commitHash, status: 'waiting' };
        items.push(item);
        added.push(item);
      }
      return added;
    },

    remove(id) {
      items = items.filter(it => it.id !== id);
    },

    reorder(id, toIndex) {
      const idx = items.findIndex(it => it.id === id);
      if (idx < 0 || toIndex < 0 || toIndex >= items.length) return;
      const [item] = items.splice(idx, 1);
      items.splice(toIndex, 0, item);
    },

    start() {
      processQueue();
    },
  };
}

module.exports = { createQueue };
```

- [ ] **Step 2: 验证队列模块可加载**

```bash
cd scripts/autoSubmit && node -e "const { createQueue } = require('./lib/queue'); const q = createQueue({}); q.add([{ problemNum: 1, branch: 'main' }]); console.log('items:', q.items.length); console.log('running:', q.running);"
```

Expected: `items: 1`, `running: false`

- [ ] **Step 3: Commit**

```bash
git add scripts/autoSubmit/lib/queue.js
git commit -m "feat(autoSubmit): 添加 lib/queue.js（提交队列状态机）"
```

---

### Task 4: 重写 server.js

**Files:**
- Modify: `scripts/autoSubmit/server.js`（完全重写）

**Interfaces:**
- Consumes: 所有 api/ 和 lib/ 模块
- Produces: HTTP server on port 3456，12 个 API 端点 + 静态文件

- [ ] **Step 1: 替换 server.js**

```js
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const fetchProblems = require('./api/fetch-problems');
const fetchRanks = require('./api/fetch-ranks');
const submit = require('./api/submit');
const queryStatus = require('./api/query-status');
const { getBranches, getBranchHead, refreshRepo } = require('./lib/git');
const { createQueue } = require('./lib/queue');

const PORT = 3456;
const STATUS_FILE = path.join(__dirname, 'data', 'status-cache.json');
const RANK_FILE = path.join(__dirname, 'data', 'rank-cache.json');
const HISTORY_FILE = path.join(__dirname, 'data', 'submit-history.json');

const PROBLEMS = {
  1:  { assignID: '46965', proNum: 1,  name: '题目一：存储管理' },
  2:  { assignID: '46965', proNum: 2,  name: '题目二：查询执行' },
  3:  { assignID: '46965', proNum: 3,  name: '题目三：唯一索引' },
  4:  { assignID: '46965', proNum: 4,  name: '题目四：查询优化与执行' },
  5:  { assignID: '46965', proNum: 5,  name: '题目五：聚合函数与分组统计' },
  6:  { assignID: '46965', proNum: 6,  name: '题目六：Union 集合算子' },
  7:  { assignID: '46965', proNum: 7,  name: '题目七：嵌套循环连接及其优化' },
  8:  { assignID: '46965', proNum: 8,  name: '题目八：事务控制语句' },
  9:  { assignID: '46965', proNum: 9,  name: '题目九：可配置的快照隔离与可串行化隔离级别' },
  10: { assignID: '46965', proNum: 10, name: '题目十：基于静态检查点的故障恢复' },
  11: { assignID: '47932', proNum: 1,  name: '性能测试' },
};

const MAX_SCORES = {
  1: 5, 2: 5, 3: 10, 4: 10, 5: 10, 6: 10, 7: 15, 8: 5, 9: 20, 10: 10, 11: 100,
};

// ===== 缓存 =====
let statusCache = null;
let rankCache = null;

try {
  if (fs.existsSync(STATUS_FILE)) statusCache = JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
} catch {}
try {
  if (fs.existsSync(RANK_FILE)) rankCache = JSON.parse(fs.readFileSync(RANK_FILE, 'utf8'));
} catch {}

function saveCache(file, data) {
  try { fs.writeFileSync(file, JSON.stringify(data, null, 2)); } catch {}
}

// ===== 分支信息抓取 =====
async function fetchBranch(assignID, proNum) {
  try {
    const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config', 'config.json'), 'utf8'));
    const cookies = Object.entries(config.cookies).map(([k, v]) => `${k}=${v}`).join('; ');
    const resp = await fetch(`https://course.educg.net/assignment/programOJPList.jsp?proNum=${proNum}&assignID=${assignID}`, {
      headers: { cookie: cookies },
    });
    const html = await resp.text();
    const m = html.match(/name="cgsoucecode"[^>]*>([^<]*)</);
    if (!m) return null;
    const bm = m[1].match(/--branch=(\S+)/);
    return bm ? bm[1] : null;
  } catch {
    return null;
  }
}

// ===== 提交历史 =====
function saveHistory(entry) {
  let history = [];
  try {
    if (fs.existsSync(HISTORY_FILE)) history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
  } catch {}
  history.push(entry);
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

// ===== 队列 =====
const queue = createQueue({
  onItemDone(item) {
    const entry = {
      id: item.result.id,
      problemNum: item.result.problemNum,
      problemName: PROBLEMS[item.result.problemNum]?.name || '',
      branch: item.result.branch,
      commitHash: item.result.commitHash,
      submitTime: item.result.submitTime,
      score: item.result.score,
      maxScore: MAX_SCORES[item.result.problemNum] || null,
      status: item.result.status,
    };
    saveHistory(entry);
    statusCache = null;
    console.log(`[队列] 题目${item.problemNum} 完成`);
  },
  onItemFail(item, err) {
    const entry = {
      id: item.result.id,
      problemNum: item.result.problemNum,
      problemName: PROBLEMS[item.result.problemNum]?.name || '',
      branch: item.result.branch,
      commitHash: item.result.commitHash,
      submitTime: item.result.submitTime,
      error: err.message,
      status: 'error',
    };
    saveHistory(entry);
    statusCache = null;
  },
});

// ===== HTTP 工具 =====
function jsonReply(res, code, data) {
  res.writeHead(code, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

function readBody(req) {
  return new Promise(resolve => {
    let body = '';
    req.on('data', d => body += d);
    req.on('end', () => resolve(body));
  });
}

// ===== HTTP 服务器 =====
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const pn = url.pathname;
  res.setHeader('Access-Control-Allow-Origin', '*');

  try {
    // === /api/status ===
    if (pn === '/api/status') {
      const forceRefresh = url.searchParams.get('refresh') === '1';
      if (!forceRefresh && statusCache) {
        return jsonReply(res, 200, statusCache);
      }

      const problems = await fetchProblems();
      const list = [];

      for (const p of problems) {
        const cfg = PROBLEMS[p.number];
        const branch = cfg ? await fetchBranch(cfg.assignID, cfg.proNum) : null;
        const commitHash = branch ? getBranchHead(branch) : null;

        list.push({
          num: p.number,
          name: cfg ? cfg.name : p.title,
          branch,
          commitHash,
          score: p.obtainedScore,
          maxScore: p.maxScore,
          feedback: p.testResult || '',
          lastSubmitTime: p.lastSubmitTime || null,
        });
      }

      statusCache = {
        data: list,
        time: new Date().toLocaleString('zh-CN', { hour12: false }),
      };
      saveCache(STATUS_FILE, statusCache);
      return jsonReply(res, 200, statusCache);
    }

    // === /api/leaderboard ===
    if (pn === '/api/leaderboard') {
      const forceRefresh = url.searchParams.get('refresh') === '1';
      if (!forceRefresh && rankCache) {
        return jsonReply(res, 200, rankCache);
      }

      const ranks = await fetchRanks();
      rankCache = {
        contest: ranks.problems,
        performance: ranks.perf,
        time: new Date().toLocaleString('zh-CN', { hour12: false }),
      };
      saveCache(RANK_FILE, rankCache);
      return jsonReply(res, 200, rankCache);
    }

    // === /api/branches ===
    if (pn === '/api/branches') {
      return jsonReply(res, 200, { branches: getBranches() });
    }

    // === /api/branch-head ===
    if (pn === '/api/branch-head' && req.method === 'GET') {
      const branch = url.searchParams.get('branch');
      if (!branch) return jsonReply(res, 400, { error: '缺少 branch 参数' });
      return jsonReply(res, 200, { branch, commitHash: getBranchHead(branch) });
    }

    // === /api/refresh-repo ===
    if (pn === '/api/refresh-repo' && req.method === 'POST') {
      const ok = refreshRepo();
      return jsonReply(res, 200, { ok, branches: ok ? getBranches() : [] });
    }

    // === /api/submit ===
    if (pn === '/api/submit' && req.method === 'POST') {
      const body = await readBody(req);
      const { problemNum, branch } = JSON.parse(body);
      if (!problemNum || !branch) {
        return jsonReply(res, 400, { error: '缺少参数: problemNum 或 branch' });
      }
      if (!PROBLEMS[problemNum]) {
        return jsonReply(res, 400, { error: `无效题目编号: ${problemNum}` });
      }

      const commitHash = getBranchHead(branch);
      const result = await submit(problemNum, branch);
      return jsonReply(res, 200, { ok: true, problemNum, branch, commitHash, submitTime: new Date().toISOString(), result });
    }

    // === /api/queue ===
    if (pn === '/api/queue' && req.method === 'GET') {
      return jsonReply(res, 200, {
        running: queue.running,
        current: queue.current,
        items: queue.items,
      });
    }

    // === /api/queue/add ===
    if (pn === '/api/queue/add' && req.method === 'POST') {
      const body = await readBody(req);
      const { items } = JSON.parse(body);
      if (!items || !Array.isArray(items) || items.length === 0) {
        return jsonReply(res, 400, { error: '缺少 items 数组' });
      }
      const valid = items.filter(it => it.problemNum && it.branch && PROBLEMS[it.problemNum]);
      const added = queue.add(valid);
      return jsonReply(res, 200, { ok: true, added });
    }

    // === /api/queue/remove ===
    if (pn === '/api/queue/remove' && req.method === 'POST') {
      const body = await readBody(req);
      const { id } = JSON.parse(body);
      queue.remove(id);
      return jsonReply(res, 200, { ok: true });
    }

    // === /api/queue/reorder ===
    if (pn === '/api/queue/reorder' && req.method === 'POST') {
      const body = await readBody(req);
      const { id, toIndex } = JSON.parse(body);
      queue.reorder(id, toIndex);
      return jsonReply(res, 200, { ok: true });
    }

    // === /api/queue/start ===
    if (pn === '/api/queue/start' && req.method === 'POST') {
      if (queue.running) {
        return jsonReply(res, 200, { ok: true, msg: '队列已在运行中' });
      }
      queue.start();
      return jsonReply(res, 200, { ok: true, msg: '队列已启动' });
    }

    // === 静态文件 ===
    if (pn === '/' || pn === '/index.html') {
      const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(html);
    }

    if (pn === '/data/submit-history.json') {
      if (fs.existsSync(HISTORY_FILE)) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        return res.end(fs.readFileSync(HISTORY_FILE, 'utf8'));
      }
      return jsonReply(res, 200, []);
    }

    res.writeHead(404);
    res.end('Not Found');
  } catch (err) {
    console.error(`[${pn}]`, err);
    jsonReply(res, 500, { error: err.message });
  }
});

server.listen(PORT, () => {
  console.log(`评测面板: http://localhost:${PORT}`);

  if (!fs.existsSync(HISTORY_FILE)) {
    fs.writeFileSync(HISTORY_FILE, '[]');
  }

  const { exec } = require('child_process');
  const cmd = process.platform === 'darwin' ? 'open' : (process.platform === 'win32' ? 'start' : 'xdg-open');
  exec(`${cmd} http://localhost:${PORT}`, () => {});
});
```

- [ ] **Step 2: 验证 server 启动**

```bash
cd scripts/autoSubmit && timeout 3 node server.js
```

Expected: 输出 `评测面板: http://localhost:3456`，无报错

- [ ] **Step 3: Commit**

```bash
git add scripts/autoSubmit/server.js
git commit -m "refactor(autoSubmit): 重写 server.js 为薄 HTTP 路由层"
```

---

### Task 5: 清理旧文件

**Files:**
- Delete: `scripts/autoSubmit/lib/shared.js`
- Delete: `scripts/autoSubmit/lib/errors.js`
- Delete: `scripts/autoSubmit/lib/retry.js`
- Delete: `scripts/autoSubmit/js/`（整个目录）
- Delete: `scripts/autoSubmit/screenshots/`（整个目录）
- Delete: `scripts/autoSubmit/docs/platform-analysis.md`
- Modify: `scripts/autoSubmit/package.json`（去 playwright）
- Modify: `scripts/autoSubmit/README.md`

- [ ] **Step 1: 删除旧文件**

```bash
rm scripts/autoSubmit/lib/shared.js
rm scripts/autoSubmit/lib/errors.js
rm scripts/autoSubmit/lib/retry.js
rm -rf scripts/autoSubmit/js
rm -rf scripts/autoSubmit/screenshots
rm scripts/autoSubmit/docs/platform-analysis.md
```

- [ ] **Step 2: 卸载 playwright，保留 cheerio**

```bash
cd scripts/autoSubmit && npm uninstall playwright
```

package.json 此时只剩 cheerio 依赖，无需手动改写。

- [ ] **Step 3: 更新 README.md**

```bash
cat > scripts/autoSubmit/README.md << 'README'
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
README
```

- [ ] **Step 4: Commit**

```bash
git add scripts/autoSubmit/
git commit -m "chore(autoSubmit): 清理 Playwright 旧代码，更新文档"
```

---

### Task 6: 集成验证

- [ ] **Step 1: 启动 server，确认无报错**

```bash
cd scripts/autoSubmit && node server.js &
sleep 2
curl -s http://localhost:3456/api/branches | head -c 200
```

Expected: 返回 JSON 格式的分支列表

- [ ] **Step 2: 测试 /api/status 端点**

```bash
curl -s 'http://localhost:3456/api/status?refresh=1' | python3 -m json.tool 2>/dev/null | head -30
```

Expected: 返回题目状态数组，包含 num/name/branch/score 等字段

- [ ] **Step 3: 测试 index.html 可访问**

```bash
curl -s http://localhost:3456/ | head -c 100
```

Expected: 返回 HTML

- [ ] **Step 4: 关闭 server**

```bash
kill %1 2>/dev/null
```

