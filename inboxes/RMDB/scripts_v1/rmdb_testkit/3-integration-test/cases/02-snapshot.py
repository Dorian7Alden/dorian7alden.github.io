"""快照隔离测试：读事务应在写事务提交前后看到正确版本。"""
from pathlib import Path
from lib.asserts import assert_no_error, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as admin, server.client() as reader, server.client() as writer:
            exec_many(
                admin,
                [
                    "set output_file off",
                    "create table s (id int, v int);",
                    "create index s (id);",
                    "insert into s values (1, 0);",
                ],
            )
            assert_no_error(reader.sql("begin"))
            if single_int(reader.sql("select v from s where id = 1;")) != 0:
                raise TestFailure("reader did not see initial value")
            assert_no_error(writer.sql("update s set v = 7 where id = 1;"))
            if single_int(reader.sql("select v from s where id = 1;")) != 0:
                raise TestFailure("snapshot reader observed later commit")
            assert_no_error(reader.sql("commit"))
            if single_int(admin.sql("select v from s where id = 1;")) != 7:
                raise TestFailure("latest committed value is not visible")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
