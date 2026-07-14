"""范围查询测试：主键字段 + 非主键字段。
OJ 要求：主键字段上的单点查询、范围查询和非主键字段上的单点查询、范围查询。
"""
from pathlib import Path

from lib.asserts import assert_no_error, exec_many, single_int, table_rows, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                # 复合主键 (a, b)，索引列 c
                "create table rq (a int, b int, c int);",
                "create index rq (a, b);",
                "insert into rq values (1, 10, 100);",
                "insert into rq values (1, 20, 200);",
                "insert into rq values (1, 30, 300);",
                "insert into rq values (2, 10, 150);",
                "insert into rq values (2, 20, 250);",
            ])

            # ---- 主键单点查询 ----
            out = c.sql("select c from rq where a = 1 and b = 20;")
            if single_int(out) != 200:
                raise TestFailure(f"主键单点查询失败:\n{out}")

            # ---- 主键范围查询 (a=固定, b>值) ----
            out = c.sql("select c from rq where a = 1 and b > 10;")
            rows = table_rows(out)
            vals = sorted(int(r[0]) for r in rows)
            if vals != [200, 300]:
                raise TestFailure(f"主键范围查询 (b>10) 失败: {vals}")

            # ---- 主键范围查询 (a=固定, b between) ----
            out = c.sql("select c from rq where a = 1 and b >= 20 and b <= 30;")
            rows = table_rows(out)
            vals = sorted(int(r[0]) for r in rows)
            if vals != [200, 300]:
                raise TestFailure(f"主键范围查询 (between) 失败: {vals}")

            # ---- 非主键单点查询 ----
            out = c.sql("select a, b from rq where c = 250;")
            rows = table_rows(out)
            if len(rows) != 1 or rows[0][0] != "2" or rows[0][1] != "20":
                raise TestFailure(f"非主键单点查询失败:\n{out}")

            # ---- 非主键范围查询 ----
            out = c.sql("select c from rq where c > 150 and c < 300;")
            rows = table_rows(out)
            vals = sorted(int(r[0]) for r in rows)
            if vals != [200, 250]:
                raise TestFailure(f"非主键范围查询失败: {vals}")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
