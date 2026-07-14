"""并发隔离测试：快照隔离 (Snapshot Isolation)。

快照隔离保证每个事务看到一致的快照，且写写冲突被阻止。
但快照隔离允许写偏斜 (Write Skew)，这与可串行化不同。
本测试验证快照隔离的正确语义：无脏读、无丢失更新、写偏斜被允许。
"""
from pathlib import Path

from lib.asserts import assert_no_error, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as admin, server.client() as tx1, server.client() as tx2:
            exec_many(admin, [
                "set output_file off",
                "create table oncall (id int, name char(16), on_duty int);",
                "create index oncall (id);",
                "insert into oncall values (1, 'alice', 1);",
                "insert into oncall values (2, 'bob', 1);",
            ])

            # 验证初始状态
            if single_int(admin.sql("select count(*) from oncall where on_duty = 1;")) != 2:
                raise TestFailure("初始状态: 应有 2 人在岗")

            # ---- 快照隔离：写写冲突检测 ----
            # 两个事务更新同一条记录，后提交者应 abort
            assert_no_error(tx1.sql("begin"))
            assert_no_error(tx2.sql("begin"))

            tx1.sql("update oncall set on_duty = 0 where id = 1;")
            # Tx2 更新同一条记录：WW 冲突在此处触发
            out_update2 = tx2.sql("update oncall set on_duty = 0 where id = 1;")

            out1 = tx1.sql("commit")
            out2 = tx2.sql("commit")

            # 同记录写写冲突：至少一方应 abort
            # 冲突在 DML 执行时触发，abort 信息在 UPDATE 或 COMMIT 响应中
            ww_aborted = ("abort" in out_update2.lower() or
                         "abort" in out1.lower() or
                         "abort" in out2.lower())
            if not ww_aborted:
                raise TestFailure(
                    "快照隔离应检测到同记录写写冲突，但双方都成功提交！"
                )

            # ---- 快照隔离：写偏斜被允许 ----
            # 重置数据
            exec_many(admin, [
                "update oncall set on_duty = 1 where id = 1;",
                "update oncall set on_duty = 1 where id = 2;",
            ])

            assert_no_error(tx1.sql("begin"))
            count1 = single_int(tx1.sql("select count(*) from oncall where on_duty = 1;"))
            if count1 != 2:
                raise TestFailure(f"Tx1 应看到 2 人在岗，实际 {count1}")

            assert_no_error(tx2.sql("begin"))
            count2 = single_int(tx2.sql("select count(*) from oncall where on_duty = 1;"))
            if count2 != 2:
                raise TestFailure(f"Tx2 应看到 2 人在岗，实际 {count2}")

            # 两人更新不同记录 — 无写写冲突
            assert_no_error(tx1.sql("update oncall set on_duty = 0 where id = 1;"))
            assert_no_error(tx2.sql("update oncall set on_duty = 0 where id = 2;"))

            out1 = tx1.sql("commit")
            out2 = tx2.sql("commit")

            # 快照隔离下写偏斜是允许的：两人都成功
            both_ok = "abort" not in out1.lower() and "abort" not in out2.lower()
            if not both_ok:
                raise TestFailure(
                    "快照隔离下不同记录的更新不应冲突，但至少一方 abort 了！"
                )

            # 验证最终状态：0 人在岗（写偏斜的后果，快照隔离允许）
            remaining = single_int(admin.sql(
                "select count(*) from oncall where on_duty = 1;"
            ))
            if remaining != 0:
                raise TestFailure(
                    f"预期写偏斜后 0 人在岗，实际 {remaining} 人在岗"
                )

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
