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
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 分钟

let statusCache = null;
let rankCache = null;

try {
  if (fs.existsSync(STATUS_FILE)) statusCache = JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
} catch {}
try {
  if (fs.existsSync(RANK_FILE)) rankCache = JSON.parse(fs.readFileSync(RANK_FILE, 'utf8'));
} catch {}

function isCacheFresh(cache) {
  if (!cache || !cache._savedAt) return false;
  return (Date.now() - new Date(cache._savedAt).getTime()) < CACHE_TTL_MS;
}

function saveCache(file, data) {
  data._savedAt = new Date().toISOString();
  try { fs.writeFileSync(file, JSON.stringify(data, null, 2)); } catch {}
}

// ===== 排行榜格式转换 =====
// fetch-ranks 返回 { columns, ranks }，前端期望 { headers, teams: [{ rank, studentId, team, school, values }] }
function transformRanks(raw) {
  if (!raw || !raw.columns || !raw.ranks) return null;
  const headers = raw.columns;
  const teams = raw.ranks.map(entry => {
    const team = {
      rank: parseInt(entry['#']) || 0,
      studentId: entry['用户名'] || '',
      team: entry['队伍'] || '',
      school: entry['学校'] || '',
      values: [],
    };
    // 剩余列按顺序放入 values
    for (const col of headers) {
      if (col === '#' || col === '用户名' || col === '队伍' || col === '学校') continue;
      team.values.push(entry[col] != null ? String(entry[col]) : '');
    }
    return team;
  });
  return { headers, teams };
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
  stateFile: path.join(__dirname, 'data', 'queue-state.json'),
  onItemDone(item) {
    const entry = {
      id: item.result.id,
      problemNum: item.result.problemNum,
      problemName: PROBLEMS[item.result.problemNum]?.name || '',
      branch: item.result.branch,
      commitHash: item.result.commitHash,
      submitTime: item.result.submitTime,
      detectTime: item.result.detectTime || null,
      elapsedMin: item.result.elapsedMin || 0,
      score: item.result.score,
      maxScore: item.result.maxScore || MAX_SCORES[item.result.problemNum] || null,
      feedback: item.result.feedback ? String(item.result.feedback).substring(0, 500) : null,
      status: item.result.status,
    };
    saveHistory(entry);
    statusCache = null;
    console.log(`[队列] 题目${item.problemNum} 完成 score=${item.result.score}`);
  },
  onItemFail(item, err) {
    const entry = {
      id: item.result.id,
      problemNum: item.result.problemNum,
      problemName: PROBLEMS[item.result.problemNum]?.name || '',
      branch: item.result.branch,
      commitHash: item.result.commitHash,
      submitTime: item.result.submitTime || new Date().toISOString(),
      detectTime: null,
      elapsedMin: 0,
      score: null,
      maxScore: null,
      feedback: null,
      status: 'failed',
      error: err.message,
    };
    saveHistory(entry);
    statusCache = null;
  },
});

// ===== HTTP 工具 =====
function jsonReply(res, code, data) {
  res.writeHead(code, {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store',
  });
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
      if (!forceRefresh && statusCache && isCacheFresh(statusCache)) {
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
      if (!forceRefresh && rankCache && isCacheFresh(rankCache)) {
        return jsonReply(res, 200, rankCache);
      }

      const ranks = await fetchRanks();
      rankCache = {
        contest: transformRanks(ranks.problems),
        performance: transformRanks(ranks.perf),
        time: new Date().toLocaleString('zh-CN', { hour12: false }),
      };
      saveCache(RANK_FILE, rankCache);
      return jsonReply(res, 200, rankCache);
    }

    // === /api/branches ===
    if (pn === '/api/branches') {
      return jsonReply(res, 200, getBranches());
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
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      return res.end(html);
    }

    if (pn === '/data/submit-history.json') {
      if (fs.existsSync(HISTORY_FILE)) {
        res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
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
