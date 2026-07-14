// TPC-C 事务: Payment — 订单付款
#include "common.h"

bool run_payment(Ctx &c, Stat *stat, bool measure) {
    int w = c.rnd(1, c.W), d = c.rnd(1, 10), cust = c.rnd(1, c.customers_per_dist);
    double amt = c.rnd(1, 5000);
    std::string r;
    char q[2048];
    bool has;

    auto step = [&](StepId step_id, const char *sql) -> bool {
        if (!timed_send(c, sql, r, stat, measure, step_id)) return false;
        if (is_failure(r)) { timed_abort(c, r, stat, measure); return false; }
        return true;
    };

    if (!timed_send(c, "begin;", r, stat, measure, STEP_BEGIN) || is_failure(r)) return false;

    snprintf(q, sizeof(q), "select w_ytd from warehouse where w_id=%d;", w);
    if (!step(PAY_SELECT_WARE_YTD, q)) return false;
    double wytd = parse_cell_double(r, has);
    if (!has) { timed_abort(c, r, stat, measure); return false; }

    snprintf(q, sizeof(q), "update warehouse set w_ytd=%.2f where w_id=%d;", wytd + amt, w);
    if (!step(PAY_UPDATE_WARE, q)) return false;

    snprintf(q, sizeof(q), "select w_street_1, w_city, w_state, w_zip, w_name from warehouse where w_id=%d;", w);
    if (!step(PAY_SELECT_WARE_INFO, q)) return false;

    snprintf(q, sizeof(q), "select d_ytd from district where d_w_id=%d and d_id=%d;", w, d);
    if (!step(PAY_SELECT_DIST_YTD, q)) return false;
    double dytd = parse_cell_double(r, has);
    if (!has) { timed_abort(c, r, stat, measure); return false; }

    snprintf(q, sizeof(q), "update district set d_ytd=%.2f where d_w_id=%d and d_id=%d;", dytd + amt, w, d);
    if (!step(PAY_UPDATE_DIST, q)) return false;

    snprintf(q, sizeof(q), "select d_street_1, d_city, d_state, d_zip, d_name from district where d_w_id=%d and d_id=%d;", w, d);
    if (!step(PAY_SELECT_DIST_INFO, q)) return false;

    snprintf(q, sizeof(q),
             "select c_balance, c_ytd_payment, c_payment_cnt, c_first, c_middle, c_last, "
             "c_street_1, c_city, c_state, c_zip, c_phone, c_credit, c_credit_lim, c_discount, c_since "
             "from customer where c_w_id=%d and c_d_id=%d and c_id=%d;", w, d, cust);
    if (!step(PAY_SELECT_CUSTOMER, q)) return false;

    double bal = 0, ytd_payment = 0;
    long payment_cnt = 0;
    if (!parse_cell_double_at(r, 0, bal) || !parse_cell_double_at(r, 1, ytd_payment) || !parse_cell_int_at(r, 2, payment_cnt)) {
        timed_abort(c, r, stat, measure);
        return false;
    }

    snprintf(q, sizeof(q),
             "update customer set c_balance=%.2f, c_ytd_payment=%.2f, c_payment_cnt=%ld "
             "where c_w_id=%d and c_d_id=%d and c_id=%d;",
             bal - amt, ytd_payment + amt, payment_cnt + 1, w, d, cust);
    if (!step(PAY_UPDATE_CUSTOMER, q)) return false;

    snprintf(q, sizeof(q), "insert into history values (%d,%d,%d,%d,%d,'2026-01-01',%.2f,'pay');", cust, d, w, d, w, amt);
    if (!step(PAY_INSERT_HISTORY, q)) return false;

    if (!timed_send(c, "commit;", r, stat, measure, STEP_COMMIT) || is_failure(r)) return false;
    return true;
}
