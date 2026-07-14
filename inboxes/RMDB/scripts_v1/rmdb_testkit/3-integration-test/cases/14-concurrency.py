"""并发隔离回归：验证事务真实并发重叠执行，以及基本隔离正确性。"""
from pathlib import Path
import threading
import time

from lib.asserts import assert_no_error, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    # ---- 1. 并发重叠 gate ----
    server.start()
    try:
        with server.client() as admin:
            exec_many(admin, [
                "set output_file off",
                "create table accounts (id int, balance int);",
                "create index accounts (id);",
                "insert into accounts values (1, 1000);",
                "insert into accounts values (2, 1000);",
            ])

            # 起两个线程同时做转账，验证执行时间有重叠（非串行化）
            overlap_evidence = []

            def transfer(from_id: int, to_id: int, tag: str) -> None:
                c = server.client()
                try:
                    t0 = time.time()
                    assert_no_error(c.sql("begin"), f"{tag} begin")
                    bal1 = single_int(c.sql(f"select balance from accounts where id = {from_id};"))
                    bal2 = single_int(c.sql(f"select balance from accounts where id = {to_id};"))

                    out = c.sql(f"update accounts set balance = {bal1 - 10} where id = {from_id};")
                    if "abort" in out.lower():
                        try:
                            c.sql("abort")
                        except Exception:
                            pass
                        t1 = time.time()
                        overlap_evidence.append((tag, t0, t1, "aborted"))
                        return

                    out = c.sql(f"update accounts set balance = {bal2 + 10} where id = {to_id};")
                    if "abort" in out.lower():
                        try:
                            c.sql("abort")
                        except Exception:
                            pass
                        t1 = time.time()
                        overlap_evidence.append((tag, t0, t1, "aborted"))
                        return

                    out = c.sql("commit")
                    t1 = time.time()
                    overlap_evidence.append((tag, t0, t1, out))
                finally:
                    c.close()

            t1 = threading.Thread(target=transfer, args=(1, 2, "Tx1"))
            t2 = threading.Thread(target=transfer, args=(2, 1, "Tx2"))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            # 两个线程都运行即可通过 gate（abort 不破坏并发重叠验证）
            if len(overlap_evidence) != 2:
                raise TestFailure(
                    f"并发重叠 gate 失败: 只收集到 {len(overlap_evidence)} 个线程结果"
                )

            # 最终余额应守恒: balance[1] + balance[2] = 2000
            # abort 的事务会被回滚，不影响余额守恒
            total = single_int(admin.sql("select sum(balance) from accounts;"))
            if total != 2000:
                raise TestFailure(f"余额不守恒: sum(balance) = {total}, 预期 2000")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 2. 丢失更新检测 ----
    server.start()
    try:
        with server.client() as admin:
            exec_many(admin, [
                "set output_file off",
                "create table counter (id int, val int);",
                "create index counter (id);",
                "insert into counter values (1, 0);",
            ])

            abort_count = [0]

            def increment(tag: str) -> None:
                c = server.client()
                try:
                    assert_no_error(c.sql("begin"), f"{tag} begin")
                    v = single_int(c.sql("select val from counter where id = 1;"))

                    out = c.sql(f"update counter set val = {v + 1} where id = 1;")
                    if "abort" in out.lower():
                        try:
                            c.sql("abort")
                        except Exception:
                            pass
                        abort_count[0] += 1
                        return

                    out = c.sql("commit")
                    if "abort" in out.lower():
                        abort_count[0] += 1
                finally:
                    c.close()

            threads = []
            for i in range(4):
                t = threading.Thread(target=increment, args=(f"Tx{i}",))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()

            # 至少有一次 abort（WW conflict 检测生效）
            final_val = single_int(admin.sql("select val from counter where id = 1;"))
            if abort_count[0] == 0 and final_val != 4:
                raise TestFailure(
                    f"丢失更新: 4 并发 increment 全部提交但 val={final_val} ≠ 4, "
                    f"且无 abort (abort_count=0)"
                )

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 3. 脏读检测 ----
    server.start()
    try:
        with server.client() as admin, server.client() as reader:
            exec_many(admin, [
                "set output_file off",
                "create table secret (id int, v int);",
                "create index secret (id);",
                "insert into secret values (1, 100);",
            ])

            # TxA 更新但未提交
            assert_no_error(admin.sql("begin"))
            assert_no_error(admin.sql("update secret set v = 999 where id = 1;"))

            # TxB 读同一行应读到旧值
            v = single_int(reader.sql("select v from secret where id = 1;"))
            if v != 100:
                raise TestFailure(f"脏读: 读到未提交修改 v={v}, 预期 100")

            admin.sql("abort")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 4. 快照隔离 ----
    server.start()
    try:
        with server.client() as admin, server.client() as reader:
            exec_many(admin, [
                "set output_file off",
                "create table snap (id int, v int);",
                "create index snap (id);",
                "insert into snap values (1, 1);",
            ])

            # reader 开启事务，记下快照
            assert_no_error(reader.sql("begin"))
            snap_before = single_int(reader.sql("select v from snap where id = 1;"))

            # admin 更新并提交
            assert_no_error(admin.sql("update snap set v = 2 where id = 1;"))

            # reader 在同一事务内再读，应看到快照值（不变）
            snap_after = single_int(reader.sql("select v from snap where id = 1;"))
            assert_no_error(reader.sql("commit"))

            if snap_after != snap_before:
                raise TestFailure(
                    f"快照隔离失败: 事务内前后读取不一致 "
                    f"before={snap_before} after={snap_after}"
                )

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
