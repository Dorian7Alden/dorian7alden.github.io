"""数据一致性检查测试。
OJ 压测后必查的三类一致性：
1. 行数校验 — 9 张表预期行数
2. 引用完整性 — new_orders→orders, order_line→orders/items, stock→warehouse/items
3. 业务约束 — w_ytd=SUM(d_ytd), s_quantity≥0, new_orders 每 district≤900
"""
from pathlib import Path

from lib.asserts import assert_no_error, exec_many, single_int, table_rows, TestFailure
from lib.server import Server

# 模拟 TPC-C schema（与 bench/schema.sql 一致）
SCHEMA = [
    "create table warehouse (w_id int, w_name char(16), w_street_1 char(32), w_city char(32), w_state char(16), w_zip char(16), w_tax float, w_ytd float);",
    "create index warehouse (w_id);",
    "create table district (d_id int, d_w_id int, d_name char(16), d_street_1 char(32), d_city char(32), d_state char(16), d_zip char(16), d_tax float, d_ytd float, d_next_o_id int);",
    "create index district (d_w_id, d_id);",
    "create table customer (c_id int, c_d_id int, c_w_id int, c_first char(16), c_middle char(2), c_last char(16), c_street_1 char(20), c_city char(20), c_state char(2), c_zip char(9), c_phone char(16), c_since char(10), c_credit char(2), c_credit_lim float, c_discount float, c_balance float, c_ytd_payment float, c_payment_cnt int, c_delivery_cnt int, c_data char(200));",
    "create index customer (c_w_id, c_d_id, c_id);",
    "create table history (h_c_id int, h_c_d_id int, h_c_w_id int, h_d_id int, h_w_id int, h_date char(10), h_amount float, h_data char(24));",
    "create table new_orders (no_o_id int, no_d_id int, no_w_id int);",
    "create index new_orders (no_w_id, no_d_id, no_o_id);",
    "create table orders (o_id int, o_c_id int, o_d_id int, o_w_id int, o_entry_d char(10), o_carrier_id int, o_ol_cnt int, o_all_local int);",
    "create index orders (o_w_id, o_d_id, o_id);",
    "create table order_line (ol_o_id int, ol_d_id int, ol_w_id int, ol_number int, ol_i_id int, ol_supply_w_id int, ol_delivery_d char(10), ol_quantity int, ol_amount float, ol_dist_info char(24));",
    "create index order_line (ol_w_id, ol_d_id, ol_o_id, ol_number);",
    "create table item (i_id int, i_im_id int, i_name char(24), i_price float, i_data char(50));",
    "create index item (i_id);",
    "create table stock (s_i_id int, s_w_id int, s_quantity int, s_dist_01 char(24), s_dist_02 char(24), s_dist_03 char(24), s_dist_04 char(24), s_dist_05 char(24), s_dist_06 char(24), s_dist_07 char(24), s_dist_08 char(24), s_dist_09 char(24), s_dist_10 char(24), s_ytd int, s_order_cnt int, s_remote_cnt int, s_data char(50));",
    "create index stock (s_w_id, s_i_id);",
]


def run(_repo: Path, server: Server) -> None:
    server.start()
    try:
        with server.client() as c:
            # ---- 建表 ----
            for sql in SCHEMA:
                assert_no_error(c.sql(sql), sql)

            # ---- 插入关联数据（W=1 规模） ----
            # warehouse: 1 行
            assert_no_error(c.sql(
                "insert into warehouse values (1, 'W1', '', '', '', '', 0.1, 300.0);"
            ))
            # district: 2 行
            assert_no_error(c.sql(
                "insert into district values (1, 1, '', '', '', '', '', 0.1, 150.0, 3);"
            ))
            assert_no_error(c.sql(
                "insert into district values (2, 1, '', '', '', '', '', 0.1, 150.0, 5);"
            ))
            # customer: 各 district 2 个
            for d_id in (1, 2):
                for c_id in (1, 2):
                    assert_no_error(c.sql(
                        f"insert into customer values ({c_id}, {d_id}, 1, '', '', '', '', '', '', '', '', '', '', 0, 0, 0, 0, 0, 0, '');"
                    ))
            # item: 3 个
            for i_id in range(1, 4):
                assert_no_error(c.sql(
                    f"insert into item values ({i_id}, 1, '', 9.99, '');"
                ))
            # stock: 每个 item × warehouse
            for i_id in range(1, 4):
                assert_no_error(c.sql(
                    f"insert into stock values ({i_id}, 1, 100, '', '', '', '', '', '', '', '', '', '', 0, 0, 0, '');"
                ))
            # orders + order_line + new_orders: 模拟 TPC-C 关系
            assert_no_error(c.sql(
                "insert into orders values (1, 1, 1, 1, '', 0, 2, 1);"
            ))
            assert_no_error(c.sql(
                "insert into order_line values (1, 1, 1, 1, 1, 1, '', 5, 9.99, '');"
            ))
            assert_no_error(c.sql(
                "insert into order_line values (1, 1, 1, 2, 2, 1, '', 3, 19.99, '');"
            ))
            assert_no_error(c.sql(
                "insert into new_orders values (1, 1, 1);"
            ))
            assert_no_error(c.sql(
                "insert into orders values (2, 2, 1, 1, '', 1, 1, 1);"
            ))
            assert_no_error(c.sql(
                "insert into order_line values (2, 1, 1, 1, 3, 1, '', 1, 5.00, '');"
            ))
            # history: 1 条
            assert_no_error(c.sql(
                "insert into history values (1, 1, 1, 1, 1, '', 50.0, '');"
            ))

            # ============================================
            # 检查 1：行数校验
            # ============================================
            checks = [
                ("warehouse", "warehouse", 1),
                ("district", "district", 2),
                ("customer", "customer", 4),
                ("history", "history", 1),
                ("orders", "orders", 2),
                ("new_orders", "new_orders", 1),
                ("order_line", "order_line", 3),
                ("item", "item", 3),
                ("stock", "stock", 3),
            ]
            for label, table, expected in checks:
                actual = single_int(c.sql(f"select count(*) from {table};"))
                if actual != expected:
                    raise TestFailure(f"行数校验 [{label}]: 预期 {expected}，实际 {actual}")

            # ============================================
            # 检查 2：引用完整性
            # ============================================
            # new_orders → orders
            out = c.sql(
                "select count(*) from new_orders no "
                "left join orders o on no.no_o_id=o.o_id and no.no_d_id=o.o_d_id and no.no_w_id=o.o_w_id "
                "where o.o_id is null;"
            )
            orphans = single_int(out)
            if orphans != 0:
                raise TestFailure(f"引用完整性 [new_orders→orders]: {orphans} 条孤立记录")

            # order_line → orders
            out = c.sql(
                "select count(*) from order_line ol "
                "left join orders o on ol.ol_o_id=o.o_id and ol.ol_d_id=o.o_d_id and ol.ol_w_id=o.o_w_id "
                "where o.o_id is null;"
            )
            orphans = single_int(out)
            if orphans != 0:
                raise TestFailure(f"引用完整性 [order_line→orders]: {orphans} 条孤立记录")

            # order_line → item
            out = c.sql(
                "select count(*) from order_line ol "
                "left join item i on ol.ol_i_id=i.i_id "
                "where i.i_id is null;"
            )
            orphans = single_int(out)
            if orphans != 0:
                raise TestFailure(f"引用完整性 [order_line→item]: {orphans} 条孤立记录")

            # stock → item
            out = c.sql(
                "select count(*) from stock s "
                "left join item i on s.s_i_id=i.i_id "
                "where i.i_id is null;"
            )
            orphans = single_int(out)
            if orphans != 0:
                raise TestFailure(f"引用完整性 [stock→item]: {orphans} 条孤立记录")

            # stock → warehouse
            out = c.sql(
                "select count(*) from stock s "
                "left join warehouse w on s.s_w_id=w.w_id "
                "where w.w_id is null;"
            )
            orphans = single_int(out)
            if orphans != 0:
                raise TestFailure(f"引用完整性 [stock→warehouse]: {orphans} 条孤立记录")

            # ============================================
            # 检查 3：业务约束
            # ============================================
            # w_ytd = SUM(d_ytd)
            out = c.sql(
                "select count(*) from ("
                "  select w.w_id, w.w_ytd, sum(d.d_ytd) as sum_d_ytd "
                "  from warehouse w join district d on d.d_w_id=w.w_id "
                "  group by w.w_id "
                ") t where w_ytd != sum_d_ytd;"
            )
            violations = single_int(out)
            if violations != 0:
                raise TestFailure(f"业务约束 [w_ytd=SUM(d_ytd)]: {violations} 条违反")

            # s_quantity >= 0
            out = c.sql("select count(*) from stock where s_quantity < 0;")
            violations = single_int(out)
            if violations != 0:
                raise TestFailure(f"业务约束 [s_quantity>=0]: {violations} 条违反")

            # new_orders 每 district 不超过 900
            out = c.sql(
                "select count(*) from ("
                "  select no_w_id, no_d_id, count(*) as cnt "
                "  from new_orders group by no_w_id, no_d_id "
                "  having cnt > 900"
                ");"
            )
            violations = single_int(out)
            if violations != 0:
                raise TestFailure(f"业务约束 [new_orders≤900 per district]: {violations} 条违反")

            # 检查订单号连续性（district.d_next_o_id 应 > 最大 o_id）
            out = c.sql(
                "select count(*) from district d "
                "where d.d_next_o_id <= ("
                "  select coalesce(max(o.o_id), 0) from orders o "
                "  where o.o_w_id=d.d_w_id and o.o_d_id=d.d_id"
                ");"
            )
            violations = single_int(out)
            if violations != 0:
                raise TestFailure(f"业务约束 [d_next_o_id>max(o_id)]: {violations} 条违反")

    finally:
        server.stop()
        server.assert_log_clean()
        server.cleanup_db()
