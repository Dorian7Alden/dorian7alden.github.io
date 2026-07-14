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
