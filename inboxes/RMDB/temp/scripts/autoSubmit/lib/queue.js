'use strict';

const fs = require('fs');
const submit = require('../api/submit');
const queryStatus = require('../api/query-status');
const fetchProblems = require('../api/fetch-problems');
const { getBranchHead } = require('./git');

function createQueue({ onItemDone, onItemFail, stateFile }) {
  let nextId = 1;
  let running = false;
  let current = null;
  let items = [];

  function save() {
    if (!stateFile) return;
    try {
      fs.writeFileSync(stateFile, JSON.stringify({ nextId, items }, null, 2));
    } catch {}
  }

  // 启动时恢复队列
  if (stateFile && fs.existsSync(stateFile)) {
    try {
      const saved = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      nextId = saved.nextId || 1;
      items = (saved.items || []).map(it => ({
        ...it,
        status: it.status === 'running' ? 'waiting' : it.status,
      }));
    } catch {}
  }

  async function processQueue() {
    if (running) return;
    if (items.length === 0) return;
    running = true;

    while (items.length > 0) {
      const item = items[0];
      item.status = 'running';
      item.startTime = new Date().toISOString();
      current = item;
      save();

      try {
        console.log(`[队列] 提交题目${item.problemNum} 分支: ${item.branch}`);
        await submit(item.problemNum, item.branch);
        const submitTime = new Date().toISOString();

        console.log(`[队列] 等待题目${item.problemNum} 评测结果...`);
        await queryStatus(item.problemNum);
        const detectTime = new Date().toISOString();

        // 提交完成后拉取最新分数
        const problems = await fetchProblems();
        const updated = problems.find(p => p.number === item.problemNum);
        const score = updated ? updated.obtainedScore : null;
        const maxScore = updated ? updated.maxScore : null;
        const feedback = updated ? (updated.testResult || '') : '';
        const elapsedMin = Math.round((Date.now() - new Date(submitTime).getTime()) / 60000);

        item.status = 'done';
        item.result = {
          id: item.id,
          problemNum: item.problemNum,
          branch: item.branch,
          commitHash: item.commitHash,
          submitTime,
          detectTime,
          elapsedMin,
          score,
          maxScore,
          feedback,
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
          status: 'failed',
        };
        if (onItemFail) await onItemFail(item, err);
      } finally {
        items.shift();
        current = null;
        save();
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
      save();
      return added;
    },

    remove(id) {
      const idx = items.findIndex(it => it.id === id);
      if (idx >= 0) items.splice(idx, 1);
      save();
    },

    reorder(id, toIndex) {
      const idx = items.findIndex(it => it.id === id);
      if (idx < 0 || toIndex < 0 || toIndex >= items.length) return;
      const [item] = items.splice(idx, 1);
      items.splice(toIndex, 0, item);
      save();
    },

    start() {
      processQueue();
    },
  };
}

module.exports = { createQueue };
