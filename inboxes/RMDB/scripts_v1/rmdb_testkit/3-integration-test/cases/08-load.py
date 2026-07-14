"""Load 命令 + set output_file off 测试。
OJ 要求：
- load file_name into table_name; 正确导入 CSV
- set output_file off 无分号命令
- set output_file on 恢复输出
"""
import tempfile
from pathlib import Path

from lib.asserts import assert_no_error, exec_many, single_int, TestFailure
from lib.server import Server


def run(repo: Path, server: Server) -> None:
    # 1) 准备 CSV 数据文件
    csv_content = "id,name,val\n1,alpha,100\n2,beta,200\n3,gamma,300\n"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, dir=repo / "build"
    ) as f:
        f.write(csv_content)
        csv_path = f.name

    try:
        server.start()
        try:
            with server.client() as c:
                # 建表
                exec_many(c, [
                    "create table load_test (id int, name char(16), val int);",
                    "create index load_test (id);",
                ])

                # ---- load 命令 ----
                # server 启动后 chdir 到 build/<db_name>/，相对路径会从该子目录查找。
                # 因此必须使用绝对路径，确保 load 能找到 CSV 文件。
                out = c.sql(f"load {csv_path} into load_test;")
                assert_no_error(out, f"load {csv_path}")

                # 验证导入行数
                count = single_int(c.sql("select count(*) from load_test;"))
                if count != 3:
                    raise TestFailure(f"load 后应有 3 行，实际 {count}")

                # 验证数据内容
                out = c.sql("select * from load_test;")
                if "alpha" not in out or "beta" not in out or "gamma" not in out:
                    raise TestFailure(f"load 数据不完整:\n{out}")

                # ---- set output_file off (无分号命令) ----
                out = c.sql("set output_file off")
                assert_no_error(out, "set output_file off")

                # 执行一条 SQL，验证仍正常返回
                out = c.sql("select val from load_test where id = 1;")
                if "100" not in out:
                    raise TestFailure(f"output_file off 后查询异常: {out}")

                # ---- set output_file on (恢复) ----
                out = c.sql("set output_file on")
                assert_no_error(out, "set output_file on")

        finally:
            server.stop()
            server.assert_log_clean()
            server.cleanup_db()
    finally:
        Path(csv_path).unlink(missing_ok=True)
