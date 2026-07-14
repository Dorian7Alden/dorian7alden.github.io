"""崩溃恢复测试：kill -9 → 重启 → 已提交的不丢，未提交的回滚。"""
from pathlib import Path
from lib.asserts import assert_no_error, exec_many, table_rows, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as c:
            exec_many(
                c,
                [
                    "set output_file off",
                    "create table rec (id int, v int);",
                    "create index rec (id);",
                    "insert into rec values (1, 100);",
                    "insert into rec values (2, 200);",
                    "begin",
                    "insert into rec values (99, 9900);",
                    "abort",
                    "insert into rec values (3, 300);",
                    "create static_checkpoint;",
                ],
            )
            # 断连一个未提交的事务
            open_tx = server.client()
            assert_no_error(open_tx.sql("begin"))
            assert_no_error(open_tx.sql("insert into rec values (88, 8800);"))
            open_tx.close()
        server.restart_same_db()
        with server.client() as c:
            rows = table_rows(c.sql("select * from rec;"))
            values = sorted((int(r[0]), int(r[1])) for r in rows)
            if values != [(1, 100), (2, 200), (3, 300)]:
                raise TestFailure(f"unexpected recovered rows: {values}")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
