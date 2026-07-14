// TPC-C 事务: Delivery — 配送
#include "common.h"

bool run_delivery(Ctx &c, Stat *stat, bool measure) {
    int w = c.rnd(1, c.W), d = c.rnd(1, 10);
    std::string r;
    char q[2048];

    auto step = [&](StepId step_id, const char *sql) -> bool {
        if (!timed_send(c, sql, r, stat, measure, step_id)) return false;
        if (is_failure(r)) { timed_abort(c, r, stat, measure); return false; }
        return true;
    };

    if (!timed_send(c, "begin;", r, stat, measure, STEP_BEGIN) || is_failure(r)) return false;

    snprintf(q, sizeof(q), "select no_o_id from new_orders where no_w_id=%d and no_d_id=%d order by no_o_id limit 1;", w, d);
    if (!step(DEL_SELECT_NEW_ORDER, q)) return false;

    bool has;
    long oid = parse_cell_int(r, has);
    if (!has) {
        // 无可配送订单：空提交
        if (!timed_send(c, "commit;", r, stat, measure, STEP_COMMIT)) return false;
        return true;
    }

    snprintf(q, sizeof(q), "delete from new_orders where no_w_id=%d and no_d_id=%d and no_o_id=%ld;", w, d, oid);
    if (!step(DEL_DELETE_NEW_ORDER, q)) return false;

    snprintf(q, sizeof(q), "select o_c_id from orders where o_w_id=%d and o_d_id=%d and o_id=%ld;", w, d, oid);
    if (!step(DEL_SELECT_ORDER_CUSTOMER, q)) return false;
    long cust = parse_cell_int(r, has);
    if (!has) { timed_abort(c, r, stat, measure); return false; }

    snprintf(q, sizeof(q), "update orders set o_carrier_id=5 where o_w_id=%d and o_d_id=%d and o_id=%ld;", w, d, oid);
    if (!step(DEL_UPDATE_ORDERS, q)) return false;

    snprintf(q, sizeof(q),
             "update order_line set ol_delivery_d='2026-01-01' where ol_w_id=%d and ol_d_id=%d and ol_o_id=%ld;", w, d, oid);
    if (!step(DEL_UPDATE_ORDER_LINE, q)) return false;

    snprintf(q, sizeof(q), "select sum(ol_amount) from order_line where ol_w_id=%d and ol_d_id=%d and ol_o_id=%ld;", w, d, oid);
    if (!step(DEL_SUM_ORDER_LINE, q)) return false;
    double sum_amount = parse_cell_double(r, has);
    if (!has) sum_amount = 0;

    snprintf(q, sizeof(q), "select c_balance, c_delivery_cnt from customer where c_w_id=%d and c_d_id=%d and c_id=%ld;", w, d, cust);
    if (!step(DEL_SELECT_CUSTOMER, q)) return false;
    double balance = 0;
    long delivery_cnt = 0;
    if (!parse_cell_double_at(r, 0, balance) || !parse_cell_int_at(r, 1, delivery_cnt)) {
        timed_abort(c, r, stat, measure);
        return false;
    }

    snprintf(q, sizeof(q),
             "update customer set c_balance=%.2f, c_delivery_cnt=%ld where c_w_id=%d and c_d_id=%d and c_id=%ld;",
             balance + sum_amount, delivery_cnt + 1, w, d, cust);
    if (!step(DEL_UPDATE_CUSTOMER, q)) return false;

    if (!timed_send(c, "commit;", r, stat, measure, STEP_COMMIT) || is_failure(r)) return false;
    return true;
}
