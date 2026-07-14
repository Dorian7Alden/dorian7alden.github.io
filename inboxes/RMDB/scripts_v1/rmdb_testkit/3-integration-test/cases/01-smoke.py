"""CRUD 冒烟测试 + 唯一索引复用。"""
from pathlib import Path
from lib.asserts import assert_no_error, assert_abort, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    # ---- smoke ----
    server.start()
    try:
        with server.client() as c:
            exec_many(
                c,
                [
                    "set output_file off",
                    "create table t (id int, v int);",
                    "create index t (id);",
                    "insert into t values (1, 10);",
                    "insert into t values (2, 20);",
                ],
            )
            if single_int(c.sql("select count(*) from t;")) != 2:
                raise TestFailure("count after insert is not 2")
            assert_no_error(c.sql("update t set v = 99 where id = 1;"))
            if single_int(c.sql("select v from t where id = 1;")) != 99:
                raise TestFailure("update result is not visible")
            assert_no_error(c.sql("delete from t where id = 2;"))
            if single_int(c.sql("select count(*) from t;")) != 1:
                raise TestFailure("count after delete is not 1")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- index reuse ----
    server.start()
    try:
        with server.client() as c:
            exec_many(
                c,
                [
                    "set output_file off",
                    "create table u (id int, v int);",
                    "create index u (id);",
                    "insert into u values (1, 10);",
                ],
            )
            dup = c.sql("insert into u values (1, 20);")
            if "unique" not in dup.lower() and "abort" not in dup.lower():
                raise TestFailure(f"duplicate unique key was accepted: {dup!r}")
            assert_no_error(c.sql("delete from u where id = 1;"))
            assert_no_error(c.sql("insert into u values (1, 30);"))
            if single_int(c.sql("select v from u where id = 1;")) != 30:
                raise TestFailure("unique key reuse after MVCC delete failed")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
