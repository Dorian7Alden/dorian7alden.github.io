"""TPC-C 五种事务功能验证。
模拟 TPC-C 事务类型，确保每种事务的基本操作能正确执行。
"""
from pathlib import Path

from lib.asserts import assert_no_error, exec_many, single_int, table_rows, TestFailure
from lib.server import Server


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as c:
            exec_many(c, [
                "set output_file off",
                # ---- 建表（模拟 TPC-C 核心表） ----
                "create table w (w_id int, w_ytd float);",
                "create index w (w_id);",
                "create table d (d_id int, d_w_id int, d_ytd float, d_next_o_id int);",
                "create index d (d_w_id, d_id);",
                "create table cust (c_id int, c_d_id int, c_w_id int, c_balance float, c_ytd_payment float, c_payment_cnt int, c_delivery_cnt int);",
                "create index cust (c_w_id, c_d_id, c_id);",
                "create table hist (h_c_id int, h_c_d_id int, h_c_w_id int, h_amount float);",
                "create table ord (o_id int, o_c_id int, o_d_id int, o_w_id int, o_carrier_id int, o_ol_cnt int);",
                "create index ord (o_w_id, o_d_id, o_id);",
                "create table no (no_o_id int, no_d_id int, no_w_id int);",
                "create index no (no_w_id, no_d_id, no_o_id);",
                "create table ol (ol_o_id int, ol_d_id int, ol_w_id int, ol_number int, ol_amount float);",
                "create index ol (ol_w_id, ol_d_id, ol_o_id, ol_number);",
                "create table st (s_i_id int, s_w_id int, s_quantity int);",
                "create index st (s_w_id, s_i_id);",
                "create table it (i_id int, i_price float);",
                "create index it (i_id);",

                # ---- 初始数据 ----
                "insert into w values (1, 0.0);",
                "insert into d values (1, 1, 0.0, 1);",
                "insert into cust values (1, 1, 1, 100.0, 0.0, 0, 0);",
                "insert into it values (1, 9.99);",
                "insert into it values (2, 19.99);",
                "insert into st values (1, 1, 100);",
                "insert into st values (2, 1, 50);",
            ])

            # ---- NewOrder: 插入订单 + order_line + new_orders ----
            assert_no_error(c.sql("begin"))
            assert_no_error(c.sql("insert into ord values (1, 1, 1, 1, 0, 2);"))
            assert_no_error(c.sql("insert into ol values (1, 1, 1, 1, 9.99);"))
            assert_no_error(c.sql("insert into ol values (1, 1, 1, 2, 19.99);"))
            assert_no_error(c.sql("insert into no values (1, 1, 1);"))
            assert_no_error(c.sql("commit"))

            # 验证 NewOrder 结果
            if single_int(c.sql("select o_ol_cnt from ord where o_id = 1;")) != 2:
                raise TestFailure("NewOrder: o_ol_cnt 应为 2")
            if single_int(c.sql("select count(*) from ol where ol_o_id = 1;")) != 2:
                raise TestFailure("NewOrder: 应有 2 条 order_line")
            if single_int(c.sql("select count(*) from no where no_o_id = 1;")) != 1:
                raise TestFailure("NewOrder: new_orders 应有 1 条")

            # ---- Payment: 更新余额 + 插入 history ----
            assert_no_error(c.sql("begin"))
            assert_no_error(c.sql("update w set w_ytd = w_ytd + 50.0 where w_id = 1;"))
            assert_no_error(c.sql("update d set d_ytd = d_ytd + 50.0 where d_w_id = 1 and d_id = 1;"))
            assert_no_error(c.sql("update cust set c_balance = c_balance - 50.0, c_ytd_payment = c_ytd_payment + 50.0, c_payment_cnt = c_payment_cnt + 1 where c_w_id = 1 and c_d_id = 1 and c_id = 1;"))
            assert_no_error(c.sql("insert into hist values (1, 1, 1, 50.0);"))
            assert_no_error(c.sql("commit"))

            # 验证 Payment 结果
            bal = c.sql("select c_balance from cust where c_id = 1;")
            if "50" not in bal:
                raise TestFailure(f"Payment: c_balance 应为 50.0:\n{bal}")
            if single_int(c.sql("select c_payment_cnt from cust where c_id = 1;")) != 1:
                raise TestFailure("Payment: c_payment_cnt 应为 1")
            if single_int(c.sql("select count(*) from hist;")) != 1:
                raise TestFailure("Payment: history 应有 1 条")

            # ---- OrderStatus: 查询订单 + order_line ----
            out = c.sql("select o_carrier_id, o_ol_cnt from ord where o_w_id = 1 and o_d_id = 1 and o_id = 1;")
            assert_no_error(out)
            out = c.sql("select ol_i_id, ol_amount from ol where ol_w_id = 1 and ol_d_id = 1 and ol_o_id = 1;")
            rows = table_rows(out)
            if len(rows) != 2:
                raise TestFailure(f"OrderStatus: 应查到 2 条 order_line，实际 {len(rows)}")

            # ---- Delivery: 删除 new_orders + 更新 orders + 更新 customer ----
            assert_no_error(c.sql("begin"))
            # 取最小的 new_order
            out = c.sql("select min(no_o_id) from no where no_w_id = 1 and no_d_id = 1;")
            min_oid = single_int(out)
            # 删除 new_orders 中的记录
            assert_no_error(c.sql(f"delete from no where no_o_id = {min_oid} and no_d_id = 1 and no_w_id = 1;"))
            # 更新 orders 的 carrier_id
            assert_no_error(c.sql(f"update ord set o_carrier_id = 1 where o_id = {min_oid};"))
            # 更新 customer 的 delivery_cnt 和 balance
            assert_no_error(c.sql("update cust set c_delivery_cnt = c_delivery_cnt + 1 where c_w_id = 1 and c_d_id = 1 and c_id = 1;"))
            assert_no_error(c.sql("commit"))

            # 验证 Delivery 结果
            if single_int(c.sql("select count(*) from no;")) != 0:
                raise TestFailure("Delivery: new_orders 应为空")
            if single_int(c.sql("select o_carrier_id from ord where o_id = 1;")) != 1:
                raise TestFailure("Delivery: o_carrier_id 应为 1")

            # ---- StockLevel: 聚合查询 ----
            out = c.sql("select count(*) from ol where ol_w_id = 1 and ol_d_id = 1 and ol_o_id >= 1 and ol_o_id < 21;")
            assert_no_error(out)

            # ---- 验证 s_quantity 非负 ----
            assert_no_error(c.sql("update st set s_quantity = s_quantity - 10 where s_i_id = 1 and s_w_id = 1;"))
            qty = c.sql("select s_quantity from st where s_i_id = 1 and s_w_id = 1;")
            if "90" not in qty:
                raise TestFailure(f"StockLevel: s_quantity 应为 90:\n{qty}")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
