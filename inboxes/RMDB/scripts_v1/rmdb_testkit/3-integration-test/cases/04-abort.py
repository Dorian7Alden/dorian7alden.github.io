"""Abort 与断连回滚测试。"""
from pathlib import Path
import time

from lib.asserts import assert_no_error, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as admin:
            exec_many(
                admin,
                [
                    "set output_file off",
                    "create table r (id int, v int);",
                    "create index r (id);",
                    "insert into r values (1, 0);",
                ],
            )
            # 显式 abort
            tx = server.client()
            assert_no_error(tx.sql("begin"))
            assert_no_error(tx.sql("update r set v = 11 where id = 1;"))
            assert_no_error(tx.sql("insert into r values (2, 22);"))
            assert_no_error(tx.sql("abort"))
            tx.close()
            if single_int(admin.sql("select v from r where id = 1;")) != 0:
                raise TestFailure("explicit abort did not restore update")
            if single_int(admin.sql("select count(*) from r;")) != 1:
                raise TestFailure("explicit abort did not remove insert")
            # 断连回滚
            tx2 = server.client()
            assert_no_error(tx2.sql("begin"))
            assert_no_error(tx2.sql("update r set v = 33 where id = 1;"))
            tx2.close()
            time.sleep(0.5)
            if single_int(admin.sql("select v from r where id = 1;")) != 0:
                raise TestFailure("disconnect did not roll back open txn")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
