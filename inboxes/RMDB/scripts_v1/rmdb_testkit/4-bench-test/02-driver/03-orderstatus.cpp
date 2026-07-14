// TPC-C 事务: OrderStatus — 最近订单查询
#include "common.h"

bool run_orderstatus(Ctx &c, Stat *stat, bool measure) {
    int w = c.rnd(1, c.W), d = c.rnd(1, 10), cust = c.rnd(1, c.customers_per_dist);
    std::string r;
    char q[2048];

    auto step = [&](StepId step_id, const char *sql) -> bool {
        if (!timed_send(c, sql, r, stat, measure, step_id)) return false;
        if (is_failure(r)) { timed_abort(c, r, stat, measure); return false; }
        return true;
    };

    if (!timed_send(c, "begin;", r, stat, measure, STEP_BEGIN) || is_failure(r)) return false;

    bool has = false;
    if (c.rnd(1, 100) <= 60) {
        std::string last = last_name_from_num(c.rnd(0, 999));
        snprintf(q, sizeof(q),
                 "select count(c_id) from customer where c_w_id=%d and c_d_id=%d and c_last='%s';", w, d, last.c_str());
        if (!step(OS_COUNT_CUSTOMER_LAST, q)) return false;

        snprintf(q, sizeof(q),
                 "select c_id, c_balance, c_first, c_middle, c_last from customer "
                 "where c_w_id=%d and c_d_id=%d and c_last='%s' order by c_first;", w, d, last.c_str());
        if (!step(OS_SELECT_CUSTOMER_LAST, q)) return false;
        long parsed_cust = parse_cell_int(r, has);
        if (has) cust = (int)parsed_cust;
    }

    if (!has) {
        snprintf(q, sizeof(q),
                 "select c_id, c_balance, c_first, c_middle, c_last from customer "
                 "where c_w_id=%d and c_d_id=%d and c_id=%d;", w, d, cust);
        if (!step(OS_SELECT_CUSTOMER_ID, q)) return false;
    }

    snprintf(q, sizeof(q),
             "select o_id, o_entry_d, o_carrier_id from orders where o_w_id=%d and o_d_id=%d and o_c_id=%d;", w, d, cust);
    if (!step(OS_SELECT_ORDERS, q)) return false;
    long oid = parse_cell_int(r, has);
    if (!has) oid = c.rnd(1, c.orders_per_dist);

    snprintf(q, sizeof(q),
             "select ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_delivery_d "
             "from order_line where ol_w_id=%d and ol_d_id=%d and ol_o_id=%ld;", w, d, oid);
    if (!step(OS_SELECT_ORDER_LINE, q)) return false;

    if (!timed_send(c, "commit;", r, stat, measure, STEP_COMMIT) || is_failure(r)) return false;
    return true;
}
