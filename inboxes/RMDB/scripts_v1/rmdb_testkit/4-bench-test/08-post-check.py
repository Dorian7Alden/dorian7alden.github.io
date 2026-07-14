#!/usr/bin/env python3
"""
bench 后正确性验证：
  1. 一致性检查 — 行数 / 引用完整性 / 业务约束
  2. 崩溃恢复 — kill -9 → 重启同一数据库 → 再次一致性检查

用于 benchmark 完成后，对压测后的数据库做 post-mortem 验证。
"""
from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# 复用集成测试 client 库
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "3-integration-test"))
from lib.client import RmdbClient  # noqa: E402


class PostCheckFailure(Exception):
    pass


class PostChecker:
    def __init__(self, port: int, W: int, data_dir: str, log_dir: str,
                 rmdb_binary: str, build_dir: str, db_name: str):
        self.port = port
        self.W = W
        self.data_dir = data_dir
        self.log_dir = log_dir
        self.rmdb_binary = rmdb_binary
        self.build_dir = build_dir
        self.db_name = db_name
        self.db_path = os.path.join(build_dir, db_name)
        self.consistency_passed_before_crash = False

    # ---- 客户端 ----
    def _client(self) -> RmdbClient:
        return RmdbClient(self.port, timeout=60.0)

    def _query_int(self, client: RmdbClient, sql: str) -> int:
        out = client.sql(sql)
        lines = out.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("|"):
                parts = [c.strip() for c in line.strip("|").split("|")]
                if len(parts) == 1:
                    try:
                        return int(parts[0])
                    except ValueError:
                        pass
        raise PostCheckFailure(f"expected single int from: {sql}\ngot:\n{out}")

    def _query_float(self, client: RmdbClient, sql: str) -> float:
        out = client.sql(sql)
        lines = out.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("|"):
                parts = [c.strip() for c in line.strip("|").split("|")]
                if len(parts) == 1:
                    try:
                        return float(parts[0])
                    except ValueError:
                        pass
        raise PostCheckFailure(f"expected single float from: {sql}\ngot:\n{out}")

    def _expect_no_data_error(self, out: str, label: str) -> None:
        """确保 SQL 响应不包含 abort/error/failure。"""
        lowered = out.strip().lower()
        if lowered == "abort" or "error" in lowered or "failure" in lowered:
            raise PostCheckFailure(f"[{label}] unexpected error:\n{out}")

    # =============================================================
    # 检查 1：行数校验
    # =============================================================
    def _check_row_counts(self, client: RmdbClient) -> None:
        cust_per_dist = 3000
        expected = [
            ("warehouse",     self.W),
            ("district",      self.W * 10),
            ("customer",      self.W * 10 * cust_per_dist),
            ("history",       self.W * 10 * cust_per_dist),
            ("orders",        self.W * 10 * 3000),
            ("new_orders",    None),  # 动态值，只打印
            ("order_line",    None),  # 动态值，只打印
            ("item",          100000),
            ("stock",         self.W * 100000),
        ]
        print("  [行数校验]")
        all_ok = True
        for table, exp in expected:
            actual = self._query_int(client, f"select count(*) from {table};")
            status = "✓" if (exp is None or actual == exp) else "✗"
            if exp is not None and actual != exp:
                all_ok = False
            exp_str = str(exp) if exp is not None else "—"
            print(f"    {status} {table}: {actual} (预期 {exp_str})")
        if not all_ok:
            raise PostCheckFailure("行数校验失败")

    # =============================================================
    # 检查 2：引用完整性
    # =============================================================
    def _check_ref_integrity(self, client: RmdbClient) -> None:
        checks = [
            ("new_orders → orders",
             "select count(*) from new_orders no "
             "left join orders o on no.no_o_id=o.o_id and no.no_d_id=o.o_d_id and no.no_w_id=o.o_w_id "
             "where o.o_id is null;"),
            ("order_line → orders",
             "select count(*) from order_line ol "
             "left join orders o on ol.ol_o_id=o.o_id and ol.ol_d_id=o.o_d_id and ol.ol_w_id=o.o_w_id "
             "where o.o_id is null;"),
            ("order_line → item",
             "select count(*) from order_line ol "
             "left join item i on ol.ol_i_id=i.i_id "
             "where i.i_id is null;"),
            ("stock → item",
             "select count(*) from stock s "
             "left join item i on s.s_i_id=i.i_id "
             "where i.i_id is null;"),
            ("stock → warehouse",
             "select count(*) from stock s "
             "left join warehouse w on s.s_w_id=w.w_id "
             "where w.w_id is null;"),
        ]
        print("  [引用完整性]")
        for label, sql in checks:
            orphans = self._query_int(client, sql)
            status = "✓" if orphans == 0 else "✗"
            print(f"    {status} {label}: {orphans} orphans")
            if orphans != 0:
                raise PostCheckFailure(f"引用完整性 [{label}]: {orphans} 条孤立记录")

    # =============================================================
    # 检查 3：业务约束
    # =============================================================
    def _check_business_rules(self, client: RmdbClient) -> None:
        print("  [业务约束]")

        # w_ytd = SUM(d_ytd)
        n = self._query_int(client,
            "select count(*) from ("
            "  select w.w_id, w.w_ytd, sum(d.d_ytd) as sum_d_ytd "
            "  from warehouse w join district d on d.d_w_id=w.w_id "
            "  group by w.w_id "
            ") t where abs(w_ytd - sum_d_ytd) > 0.01;")
        print(f"    {'✓' if n == 0 else '✗'} w_ytd = SUM(d_ytd): {n} violations")

        # s_quantity >= 0
        n = self._query_int(client, "select count(*) from stock where s_quantity < 0;")
        print(f"    {'✓' if n == 0 else '✗'} s_quantity >= 0: {n} violations")

        # new_orders 每 district 不超过 900
        n = self._query_int(client,
            "select count(*) from ("
            "  select no_w_id, no_d_id, count(*) as cnt "
            "  from new_orders group by no_w_id, no_d_id "
            "  having cnt > 900);")
        print(f"    {'✓' if n == 0 else '✗'} new_orders per district <= 900: {n} violations")

        # d_next_o_id > max(o_id)
        n = self._query_int(client,
            "select count(*) from district d "
            "where d.d_next_o_id <= ("
            "  select coalesce(max(o.o_id), 0) from orders o "
            "  where o.o_w_id=d.d_w_id and o.o_d_id=d.d_id);")
        print(f"    {'✓' if n == 0 else '✗'} d_next_o_id > max(o_id): {n} violations")

        # 汇总
        total = sum([
            self._query_int(client,
                "select count(*) from (select w.w_id from warehouse w "
                "join district d on d.d_w_id=w.w_id group by w.w_id "
                ") t where abs(w_ytd - sum_d_ytd) > 0.01;"),
            self._query_int(client, "select count(*) from stock where s_quantity < 0;"),
            self._query_int(client,
                "select count(*) from (select no_w_id, no_d_id, count(*) as cnt "
                "from new_orders group by no_w_id, no_d_id having cnt > 900);"),
            self._query_int(client,
                "select count(*) from district d where d.d_next_o_id <= "
                "(select coalesce(max(o.o_id), 0) from orders o "
                "where o.o_w_id=d.d_w_id and o.o_d_id=d.d_id);"),
        ])
        if total > 0:
            raise PostCheckFailure(f"业务约束检查失败: {total} violations total")

    # =============================================================
    # 检查 4：深度业务不变量（paranoid）
    # =============================================================
    def _check_business_invariants(self, client: RmdbClient) -> None:
        print("  [深度业务不变量]")

        # (a) d_next_o_id 连续性：每个 district 的订单号从 1 到 d_next_o_id-1 无跳跃
        #     检查 max(o_id) + new_orders_count + 1 = d_next_o_id
        n = self._query_int(client,
            "select count(*) from ("
            "  select d.d_w_id, d.d_id, d.d_next_o_id, "
            "    (select count(*) from orders o "
            "     where o.o_w_id=d.d_w_id and o.o_d_id=d.d_id) as order_cnt, "
            "    (select count(*) from new_orders no "
            "     where no.no_w_id=d.d_w_id and no.no_d_id=d.d_id) as new_cnt "
            "  from district d"
            ") t where t.order_cnt + t.new_cnt + 1 != t.d_next_o_id;")
        print(f"    {'✓' if n == 0 else '✗'} d_next_o_id 连续性: {n} violations")

        # (b) O_OL_CNT = 实际 order_line 行数
        n = self._query_int(client,
            "select count(*) from ("
            "  select o.o_id, o.o_d_id, o.o_w_id, o.o_ol_cnt, "
            "    (select count(*) from order_line ol "
            "     where ol.ol_o_id=o.o_id and ol.ol_d_id=o.o_d_id "
            "       and ol.ol_w_id=o.o_w_id) as actual_cnt "
            "  from orders o"
            ") t where t.o_ol_cnt != t.actual_cnt;")
        print(f"    {'✓' if n == 0 else '✗'} O_OL_CNT 匹配: {n} violations")

        # (c) O_CARRIER_ID 与 delivery 状态一致
        #     已完成 delivery 的订单 O_CARRIER_ID 非 NULL，未完成的为 NULL
        n = self._query_int(client,
            "select count(*) from orders o "
            "left join new_orders no on o.o_id=no.no_o_id "
            "  and o.o_d_id=no.no_d_id and o.o_w_id=no.no_w_id "
            "where (no.no_o_id is not null and o.o_carrier_id is not null) "
            "   or (no.no_o_id is null and o.o_carrier_id is null);")
        print(f"    {'✓' if n == 0 else '✗'} O_CARRIER_ID 一致性: {n} violations")

        # (d) OL_AMOUNT = quantity * price（浮点容差 0.01）
        n = self._query_int(client,
            "select count(*) from order_line ol "
            "join item i on ol.ol_i_id=i.i_id "
            "where abs(ol.ol_amount - ol.ol_quantity * i.i_price) > 0.01;")
        print(f"    {'✓' if n == 0 else '✗'} OL_AMOUNT 计算: {n} violations")

        # (e) C_BALANCE 合理性：不应为负数（初始值 + payment - delivery）
        n = self._query_int(client,
            "select count(*) from customer where c_balance < -0.01;")
        print(f"    {'✓' if n == 0 else '✗'} C_BALANCE >= 0: {n} violations")

        # (f) STOCK 行数 = W * 100000
        expected_stock = self.W * 100000
        actual_stock = self._query_int(client, "select count(*) from stock;")
        ok = actual_stock == expected_stock
        print(f"    {'✓' if ok else '✗'} STOCK 行数: {actual_stock} (预期 {expected_stock})")
        if not ok:
            print(f"        !! stock 行数不匹配")

        # (g) ITEM 行数 = 100000
        actual_item = self._query_int(client, "select count(*) from item;")
        ok2 = actual_item == 100000
        print(f"    {'✓' if ok2 else '✗'} ITEM 行数: {actual_item} (预期 100000)")

        # (h) HISTORY 行数 >= CUSTOMER 行数（每条 customer 至少有一次 payment）
        hist_cnt = self._query_int(client, "select count(*) from history;")
        cust_cnt = self._query_int(client, "select count(*) from customer;")
        ok3 = hist_cnt >= cust_cnt
        print(f"    {'✓' if ok3 else '✗'} HISTORY >= CUSTOMER: history={hist_cnt} customer={cust_cnt}")

        # 汇总
        violations = sum([
            n,  # d_next_o_id
            self._query_int(client,
                "select count(*) from ("
                "  select o.o_id, o.o_d_id, o.o_w_id, o.o_ol_cnt, "
                "    (select count(*) from order_line ol "
                "     where ol.ol_o_id=o.o_id and ol.ol_d_id=o.o_d_id "
                "       and ol.ol_w_id=o.o_w_id) as actual_cnt "
                "  from orders o"
                ") t where t.o_ol_cnt != t.actual_cnt;"),
            self._query_int(client,
                "select count(*) from orders o "
                "left join new_orders no on o.o_id=no.no_o_id "
                "  and o.o_d_id=no.no_d_id and o.o_w_id=no.no_w_id "
                "where (no.no_o_id is not null and o.o_carrier_id is not null) "
                "   or (no.no_o_id is null and o.o_carrier_id is null);"),
            self._query_int(client,
                "select count(*) from order_line ol "
                "join item i on ol.ol_i_id=i.i_id "
                "where abs(ol.ol_amount - ol.ol_quantity * i.i_price) > 0.01;"),
            self._query_int(client,
                "select count(*) from customer where c_balance < -0.01;"),
            0 if actual_stock == expected_stock else 1,
            0 if actual_item == 100000 else 1,
            0 if hist_cnt >= cust_cnt else 1,
        ])
        if violations > 0:
            raise PostCheckFailure(f"深度业务不变量检查失败: {violations} violations total")

    # =============================================================
    # 完整一致性检查
    # =============================================================
    def run_consistency_checks(self, label: str) -> None:
        print(f"\n--- {label} ---")
        with self._client() as client:
            self._check_row_counts(client)
            self._check_ref_integrity(client)
            self._check_business_rules(client)
            self._check_business_invariants(client)  # 新增：深度检查
        print(f"  {label}: 全部通过 ✓")

    # =============================================================
    # 崩溃恢复
    # =============================================================
    def crash_and_recover(self) -> None:
        print(f"\n--- 崩溃恢复 (kill -9) ---")

        # 1. 找到 server 进程
        result = subprocess.run(
            ["pgrep", "-f", f"bin/rmdb {self.db_name}"],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split()
        if not pids:
            # 回退：杀掉所有 rmdb
            print("  pgrep 未找到进程，回退到 pkill -x rmdb")
            subprocess.run(["pkill", "-9", "-x", "rmdb"], capture_output=True)
        else:
            for pid in pids:
                print(f"  kill -9 {pid}")
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass

        time.sleep(1.0)

        # 2. 重启 server（同一数据库目录，不清理）
        server_log = os.path.join(self.log_dir, "recovery.server.log")
        print(f"  重启 server (db={self.db_name})")
        proc = subprocess.Popen(
            [self.rmdb_binary, self.db_name],
            cwd=self.build_dir,
            stdin=subprocess.DEVNULL,
            stdout=open(server_log, "wb"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        # 3. 等待就绪
        deadline = time.time() + 15.0
        ready = False
        while time.time() < deadline:
            if proc.poll() is not None:
                print(f"  !! server 提前退出 (exit={proc.returncode})")
                with open(server_log) as f:
                    tail = f.readlines()[-20:]
                print("  last 20 lines:")
                for line in tail:
                    print(f"    {line.rstrip()}")
                raise PostCheckFailure("崩溃恢复: server 退出")
            try:
                s = __import__("socket").create_connection(("127.0.0.1", self.port), timeout=0.3)
                s.close()
                ready = True
                break
            except OSError:
                time.sleep(0.2)

        if not ready:
            proc.kill()
            raise PostCheckFailure("崩溃恢复: server 未在超时时间内就绪")

        print("  server 已就绪")

        try:
            # 4. 重新运行一致性检查
            self.run_consistency_checks("崩溃恢复后一致性检查")
            print("\n  崩溃恢复验证通过 ✓")
        finally:
            # 正常停掉 server
            try:
                os.killpg(proc.pid, signal.SIGINT)
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
                proc.wait(timeout=5)

        # 清理数据库（bench 后续不再需要）
        shutil.rmtree(self.db_path, ignore_errors=True)

    # =============================================================
    # 主入口
    # =============================================================
    def run(self) -> int:
        # Phase 1: 一致性检查（server 仍在运行）
        self.run_consistency_checks("压测后一致性检查")

        # Phase 2: 崩溃恢复
        self.crash_and_recover()

        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Bench 后正确性验证")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--W", type=int, required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--log-dir", required=True)
    args = parser.parse_args()

    rmdb_root = os.environ.get(
        "RMDB_ROOT",
        str(Path(__file__).resolve().parents[3])
    )
    build_dir = os.path.join(rmdb_root, "build")
    rmdb_binary = os.path.join(build_dir, "bin", "rmdb")
    db_name = "tpcc_bench_db"

    checker = PostChecker(
        port=args.port,
        W=args.W,
        data_dir=args.data_dir,
        log_dir=args.log_dir,
        rmdb_binary=rmdb_binary,
        build_dir=build_dir,
        db_name=db_name,
    )
    return checker.run()


if __name__ == "__main__":
    raise SystemExit(main())
