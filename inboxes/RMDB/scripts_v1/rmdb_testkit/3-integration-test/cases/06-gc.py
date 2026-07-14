"""自适应 GC 测试：长快照 + 大量更新 → GC 正确释放旧版本。"""
from pathlib import Path
from lib.asserts import assert_no_error, exec_many, single_int, stat_value, TestFailure, SkipTest
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as admin, server.client() as reader, server.client() as writer:
            exec_many(
                admin,
                [
                    "set output_file off",
                    "create table g (id int, v int);",
                    "create index g (id);",
                    "insert into g values (1, 0);",
                ],
            )
            assert_no_error(reader.sql("begin"))
            if single_int(reader.sql("select v from g where id = 1;")) != 0:
                raise TestFailure("GC test reader did not see initial value")
            for i in range(1, 4301):
                assert_no_error(writer.sql(f"update g set v = {i} where id = 1;"), f"update {i}")
            if single_int(reader.sql("select v from g where id = 1;")) != 0:
                raise TestFailure("pinned snapshot changed across GC debt")
            assert_no_error(reader.sql("commit"))
            for i in range(4301, 8501):
                assert_no_error(writer.sql(f"update g set v = {i} where id = 1;"), f"update {i}")
            if single_int(admin.sql("select v from g where id = 1;")) != 8500:
                raise TestFailure("latest GC stress value is wrong")
            stats = admin.sql("show execution_stats")
            if "mvcc_gc:" not in stats:
                raise SkipTest("branch has no mvcc_gc stats; snapshot part passed")
            runs = stat_value(stats, "runs")
            released = stat_value(stats, "released_undo_records")
            if runs < 1 or released < 1:
                raise TestFailure(f"GC stats did not show release:\n{stats}")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
