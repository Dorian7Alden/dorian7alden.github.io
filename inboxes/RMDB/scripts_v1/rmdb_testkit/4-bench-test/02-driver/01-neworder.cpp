// TPC-C 事务: NewOrder — 新订单生成
#include "common.h"

bool run_neworder(Ctx &c, Stat *stat, bool measure) {
    int w = c.rnd(1, c.W), d = c.rnd(1, 10), cust = c.rnd(1, c.customers_per_dist), ol = c.rnd(5, 15);
    std::string r;
    char q[2048];
    bool has;
    std::vector<int> item_ids(ol + 1), supply_ws(ol + 1);
    int all_local = 1;
    for (int n = 1; n <= ol; n++) {
        item_ids[n] = c.rnd(1, c.items);
        supply_ws[n] = w;
        if (c.W > 1 && c.rnd(1, 100) == 1) {
            do { supply_ws[n] = c.rnd(1, c.W); } while (supply_ws[n] == w);
            all_local = 0;
        }
    }

    auto step = [&](StepId step_id, const char *sql) -> bool {
        if (!timed_send(c, sql, r, stat, measure, step_id)) return false;
        if (is_failure(r)) { timed_abort(c, r, stat, measure); return false; }
        return true;
    };

    if (!timed_send(c, "begin;", r, stat, measure, STEP_BEGIN) || is_failure(r)) return false;

    snprintf(q, sizeof(q),
             "select c_discount, c_last, c_credit, w_tax from customer, warehouse "
             "where w_id=%d and c_w_id=w_id and c_d_id=%d and c_id=%d;", w, d, cust);
    if (!step(NO_SELECT_CUST_WARE, q)) return false;

    snprintf(q, sizeof(q), "select d_next_o_id from district where d_w_id=%d and d_id=%d;", w, d);
    if (!step(NO_SELECT_DISTRICT, q)) return false;
    long oid = parse_cell_int(r, has);
    if (!has) { timed_abort(c, r, stat, measure); return false; }

    snprintf(q, sizeof(q), "update district set d_next_o_id=%ld where d_w_id=%d and d_id=%d;", oid + 1, w, d);
    if (!step(NO_UPDATE_DISTRICT, q)) return false;

    snprintf(q, sizeof(q),
             "insert into orders values (%ld,%d,%d,%d,'2026-01-01',0,%d,%d);", oid, cust, d, w, ol, all_local);
    if (!step(NO_INSERT_ORDERS, q)) return false;

    snprintf(q, sizeof(q), "insert into new_orders values (%ld,%d,%d);", oid, d, w);
    if (!step(NO_INSERT_NEW_ORDERS, q)) return false;

    for (int n = 1; n <= ol; n++) {
        int iid = item_ids[n], supply_w = supply_ws[n];
        snprintf(q, sizeof(q), "select i_price, i_name, i_data from item where i_id=%d;", iid);
        if (!step(NO_SELECT_ITEM, q)) return false;

        snprintf(q, sizeof(q),
                 "select s_quantity, s_data, s_dist_01, s_dist_02, s_dist_03, s_dist_04, s_dist_05, "
                 "s_dist_06, s_dist_07, s_dist_08, s_dist_09, s_dist_10 "
                 "from stock where s_w_id=%d and s_i_id=%d;", supply_w, iid);
        if (!step(NO_SELECT_STOCK, q)) return false;
        long qty = parse_cell_int(r, has);
        if (has) {
            long nq = qty - 5 > 0 ? qty - 5 : qty + 91;
            snprintf(q, sizeof(q), "update stock set s_quantity=%ld where s_w_id=%d and s_i_id=%d;", nq, supply_w, iid);
            if (!step(NO_UPDATE_STOCK, q)) return false;
        }

        snprintf(q, sizeof(q),
                 "insert into order_line values (%ld,%d,%d,%d,%d,%d,'',5,10.00,'dist');", oid, d, w, n, iid, supply_w);
        if (!step(NO_INSERT_ORDER_LINE, q)) return false;
    }

    if (!timed_send(c, "commit;", r, stat, measure, STEP_COMMIT) || is_failure(r)) return false;
    return true;
}
