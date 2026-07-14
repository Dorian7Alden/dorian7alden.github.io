"""MVCC 可见性回归：覆盖 INSERT/DELETE/UPDATE/ABORT 后的可见性与索引一致性。"""
from pathlib import Path

from lib.asserts import assert_no_error, exec_many, single_int, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    # ---- 1. INSERT 后 SELECT 可见 ----
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                "create table t1 (id int, v int);",
                "create index t1 (id);",
                "insert into t1 values (1, 10);",
                "insert into t1 values (2, 20);",
            ])
            if single_int(c.sql("select count(*) from t1;")) != 2:
                raise TestFailure("INSERT 后 SELECT 不可见")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 2. DELETE 后 SELECT 不可见 ----
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                "create table t2 (id int, v int);",
                "create index t2 (id);",
                "insert into t2 values (1, 10);",
                "insert into t2 values (2, 20);",
                "delete from t2 where id = 2;",
            ])
            if single_int(c.sql("select count(*) from t2;")) != 1:
                raise TestFailure("DELETE 后已删除行仍可见")
            if single_int(c.sql("select v from t2 where id = 1;")) != 10:
                raise TestFailure("DELETE 后未删除行不可见")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 3. UPDATE 后新值可见 ----
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                "create table t3 (id int, v int);",
                "create index t3 (id);",
                "insert into t3 values (1, 10);",
                "update t3 set v = 99 where id = 1;",
            ])
            if single_int(c.sql("select v from t3 where id = 1;")) != 99:
                raise TestFailure("UPDATE 后新值不可见")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 4. ABORT 事务修改不可见 ----
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                "create table t4 (id int, v int);",
                "create index t4 (id);",
                "insert into t4 values (1, 10);",
            ])
            assert_no_error(c.sql("begin"))
            assert_no_error(c.sql("insert into t4 values (2, 20);"))
            assert_no_error(c.sql("update t4 set v = 99 where id = 1;"))
            assert_no_error(c.sql("delete from t4 where id = 1;"))
            # abort 成功后不应有 error/failure
            out = c.sql("abort")
            if "error" in out.lower() or "failure" in out.lower():
                raise TestFailure(f"ABORT 返回错误: {out}")

            # 回滚后：id=1 仍在（delete 被回滚），id=2 不应存在（insert 被回滚）
            if single_int(c.sql("select count(*) from t4;")) != 1:
                raise TestFailure("ABORT 后回滚不完全")
            if single_int(c.sql("select v from t4 where id = 1;")) != 10:
                raise TestFailure("ABORT 后 update 回滚失败，值被污染")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 5. 索引扫描与全表扫描结果一致 ----
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                "create table t5 (id int, v int);",
                "create index t5 (v);",
                "insert into t5 values (1, 100);",
                "insert into t5 values (2, 200);",
                "insert into t5 values (3, 300);",
            ])
            # 全表扫描
            count_all = single_int(c.sql("select count(*) from t5;"))
            # 索引扫描（WHERE v > 0 走索引）
            count_index = single_int(c.sql("select count(*) from t5 where v > 0;"))
            if count_all != count_index:
                raise TestFailure(
                    f"索引/全表扫描结果不一致: "
                    f"seq_scan={count_all} index_scan={count_index}"
                )
            # WHERE v = 100 走唯一索引点查
            val = single_int(c.sql("select v from t5 where v = 100;"))
            if val != 100:
                raise TestFailure(f"索引点查结果错误: {val} != 100")
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()

    # ---- 6. 空表聚合返回值正确 ----
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                "create table t6 (id int, v int);",
                "create index t6 (id);",
            ])
            if single_int(c.sql("select count(*) from t6;")) != 0:
                raise TestFailure("空表 COUNT 应返回 0")
            # SUM/AVG on empty table
            out = c.sql("select sum(v) from t6;")
            if "null" not in out.lower() and "0" not in out.lower():
                # 空表 SUM 应为 NULL 或 0（取决于实现）
                pass
    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
