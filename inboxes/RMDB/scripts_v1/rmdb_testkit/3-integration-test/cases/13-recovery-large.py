"""大数据量崩溃恢复测试。
OJ 会在 W=50 数据上做崩溃恢复，当前 05-recovery 只有 3 行。
本测试创建数百行数据、混合已提交/未提交/已回滚事务，kill-9 后验证恢复。
"""
from pathlib import Path

from lib.asserts import assert_no_error, single_int, table_rows, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as c:
            assert_no_error(c.sql("set output_file off"))
            assert_no_error(c.sql("create table big (id int, val int);"))
            assert_no_error(c.sql("create index big (id);"))

            # 已提交数据：插入 500 行
            for i in range(1, 501):
                assert_no_error(c.sql(f"insert into big values ({i}, {i * 10});"),
                                f"insert {i}")

            # 显式 abort 的行（不应恢复）
            assert_no_error(c.sql("begin"))
            assert_no_error(c.sql("insert into big values (999, 9990);"))
            assert_no_error(c.sql("abort"))

            # 未提交的行（不应恢复）
            open_tx = server.client()
            assert_no_error(open_tx.sql("begin"))
            assert_no_error(open_tx.sql("insert into big values (888, 8880);"))
            open_tx.close()

            # checkpoint
            assert_no_error(c.sql("create static_checkpoint;"))

            # 再插入一批已提交数据
            for i in range(501, 601):
                assert_no_error(c.sql(f"insert into big values ({i}, {i * 10});"),
                                f"insert {i}")

        # kill -9 崩溃
        server.restart_same_db()

        with server.client() as c:
            # 恢复后应有 600 行（500 初始 + 100 第二批）
            count = single_int(c.sql("select count(*) from big;"))
            if count != 600:
                raise TestFailure(
                    f"大数据恢复: 预期 600 行 (500 初始 + 100 checkpoint后)，实际 {count}"
                )

            # 确认 999 和 888 没有恢复
            out = c.sql("select count(*) from big where id = 999;")
            if single_int(out) != 0:
                raise TestFailure("大数据恢复: abort 的行 (id=999) 不应恢复")

            out = c.sql("select count(*) from big where id = 888;")
            if single_int(out) != 0:
                raise TestFailure("大数据恢复: 未提交的行 (id=888) 不应恢复")

            # 抽查数据完整性
            out = c.sql("select val from big where id = 500;")
            if "5000" not in out:
                raise TestFailure(f"大数据恢复: id=500 数据损坏:\n{out}")

            out = c.sql("select val from big where id = 600;")
            if "6000" not in out:
                raise TestFailure(f"大数据恢复: id=600 checkpoint后数据损坏:\n{out}")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
