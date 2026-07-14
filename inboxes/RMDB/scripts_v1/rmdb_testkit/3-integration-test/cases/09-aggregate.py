"""聚合函数测试，含字符串 min/max。
OJ 明确要求：聚合函数测试中需要考虑字符串的 min 和 max。
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
                "create table agg (id int, name char(16), score int);",
                "create index agg (id);",
                "insert into agg values (1, 'zebra', 10);",
                "insert into agg values (2, 'apple', 30);",
                "insert into agg values (3, 'mango', 20);",
            ])

            # ---- 数值聚合 ----
            if single_int(c.sql("select count(*) from agg;")) != 3:
                raise TestFailure("count(*) != 3")

            if single_int(c.sql("select sum(score) from agg;")) != 60:
                raise TestFailure("sum(score) != 60")

            val = c.sql("select min(score) from agg;")
            if "10" not in val:
                raise TestFailure(f"min(score) 应为 10:\n{val}")

            val = c.sql("select max(score) from agg;")
            if "30" not in val:
                raise TestFailure(f"max(score) 应为 30:\n{val}")

            # ---- 字符串 min/max (OJ 明确要求) ----
            val = c.sql("select min(name) from agg;")
            if "apple" not in val.lower():
                raise TestFailure(f"min(name) 应为 apple:\n{val}")

            val = c.sql("select max(name) from agg;")
            if "zebra" not in val.lower():
                raise TestFailure(f"max(name) 应为 zebra:\n{val}")

            # ---- group by + 聚合 ----
            exec_many(c, [
                "create table agg2 (grp int, val int);",
                "insert into agg2 values (1, 5);",
                "insert into agg2 values (1, 15);",
                "insert into agg2 values (2, 7);",
                "insert into agg2 values (2, 3);",
            ])
            out = c.sql("select grp, sum(val) from agg2 group by grp;")
            rows = table_rows(out)
            sums = {}
            for r in rows:
                if len(r) >= 2:
                    try:
                        k = int(r[0])
                        v = int(r[1])
                        sums[k] = v
                    except ValueError:
                        pass
            if sums.get(1) != 20 or sums.get(2) != 10:
                raise TestFailure(f"group by sum 结果错误: {sums}")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
