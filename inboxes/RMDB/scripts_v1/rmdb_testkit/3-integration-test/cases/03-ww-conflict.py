"""写写冲突测试：两个事务并发更新同一行，后者应 abort。"""
from pathlib import Path
from lib.asserts import assert_no_error, assert_abort, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as admin, server.client() as a, server.client() as b:
            exec_many(
                admin,
                [
                    "set output_file off",
                    "create table w (id int, v int);",
                    "create index w (id);",
                    "insert into w values (1, 0);",
                ],
            )
            assert_no_error(a.sql("begin"))
            assert_no_error(a.sql("update w set v = 1 where id = 1;"))
            assert_no_error(b.sql("begin"))
            assert_abort(b.sql("update w set v = 2 where id = 1;"))
            assert_no_error(a.sql("commit"))
            if single_int(admin.sql("select v from w where id = 1;")) != 1:
                raise TestFailure("winner update was not committed")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
