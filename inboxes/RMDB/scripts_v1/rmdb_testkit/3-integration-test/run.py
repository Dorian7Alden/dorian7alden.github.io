#!/usr/bin/env python3
"""集成测试入口：遍历 cases/ 逐个执行。"""
from __future__ import annotations

import argparse
import importlib.machinery
import shutil
import sys
import tempfile
import time
from pathlib import Path

from lib.server import Server

PORT_DEFAULT = 8765
CASES_DIR = Path(__file__).resolve().parent / "cases"

# 测试用例注册表：{ key: (filename, display_name) }
# 按编号排列，即执行顺序。
CASES = {
    "smoke":          ("01-smoke.py",          "CRUD + 唯一索引复用"),
    "snapshot":       ("02-snapshot.py",       "快照隔离"),
    "ww_conflict":    ("03-ww-conflict.py",    "写写冲突"),
    "abort":          ("04-abort.py",          "Abort / 断连回滚"),
    "recovery":       ("05-recovery.py",       "崩溃恢复（小数据）"),
    "gc":             ("06-gc.py",             "自适应 GC"),
    "isolation":      ("07-isolation.py",      "并发隔离（写偏斜）"),
    "load":           ("08-load.py",           "Load 命令 + output_file"),
    "aggregate":      ("09-aggregate.py",      "聚合函数（含字符串 min/max）"),
    "range_query":    ("10-range-query.py",    "范围查询"),
    "txn_function":   ("11-txn-function.py",   "TPC-C 事务功能"),
    "consistency":    ("12-consistency.py",    "数据一致性检查"),
    "recovery_large": ("13-recovery-large.py", "崩溃恢复（大数据量）"),
    "concurrency":    ("14-concurrency.py",    "并发隔离回归"),
    "mvcc":           ("15-mvcc-regression.py","MVCC 可见性回归"),
}

SUITES = {
    "quick":       ["smoke", "recovery"],
    "mvcc":        ["snapshot", "ww_conflict", "abort", "isolation", "gc"],
    "executor":    ["smoke", "aggregate", "range_query", "mvcc"],
    "concurrency": ["concurrency"],
    "correct":     ["smoke", "load", "aggregate", "range_query", "txn_function",
                    "consistency", "recovery", "recovery_large"],
    "oj":          ["load", "aggregate", "range_query", "txn_function",
                    "consistency", "recovery_large", "isolation"],
    "full":        list(CASES.keys()),
}


def resolve_repo(arg: str) -> Path:
    p = Path(arg).expanduser().resolve()
    if (p / "CMakeLists.txt").exists() and (p / "src").is_dir():
        return p
    raise SystemExit(f"not an rmdb repository: {p}")


def main() -> int:
    default_repo = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description="Run RMDB integration tests")
    parser.add_argument("--repo", default=str(default_repo), help="path to rmdb repository")
    parser.add_argument("--port", type=int, default=PORT_DEFAULT)
    parser.add_argument("--suite", choices=sorted(SUITES), default="quick")
    parser.add_argument("--test", action="append", choices=sorted(CASES), help="run selected test(s)")
    parser.add_argument("--keep-logs", action="store_true", help="keep /tmp log directory after success")
    parser.add_argument("--log-dir", default=None, help="use this directory for logs instead of /tmp")
    args = parser.parse_args()

    repo = resolve_repo(args.repo)
    selected = args.test or list(SUITES[args.suite])

    if args.log_dir:
        log_dir = Path(args.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
    else:
        log_dir = Path(tempfile.mkdtemp(prefix="rmdb_integration_"))
    results: list[dict] = []
    print(f"repo: {repo}")
    print(f"logs: {log_dir}")
    print(f"suite: {args.suite}; tests: {' '.join(selected)}")

    for key in selected:
        filename, display = CASES[key]
        start = time.time()
        status = "PASS"
        detail = ""
        print(f"==> {display} ({key})")
        try:
            mod = importlib.machinery.SourceFileLoader(key, str(CASES_DIR / filename)).load_module()
            server = Server(repo, args.port, log_dir, key)
            mod.run(repo, server)
        except SystemExit:
            raise
        except Exception as exc:
            # SkipTest 类需要从 lib.asserts 导入，这里简单按类名判断
            if type(exc).__name__ == "SkipTest":
                status = "SKIP"
                detail = str(exc)
            else:
                status = "FAIL"
                detail = str(exc)
        seconds = time.time() - start
        results.append({"name": key, "status": status, "detail": detail, "seconds": seconds})
        print(f"  [{status}] {key} ({seconds:.2f}s)" + (f" - {detail}" if detail else ""))
        if status == "FAIL":
            break

    passed = sum(1 for r in results if r["status"] == "PASS")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print("")
    print(f"summary: {passed} PASS, {skipped} SKIP, {failed} FAIL")
    if failed == 0 and not args.log_dir:
        # 仅在使用临时目录时才清理；显式 --log-dir 不删
        shutil.rmtree(log_dir, ignore_errors=True)
    elif failed != 0:
        print(f"failure logs retained at: {log_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
