// TPC-C 事务: StockLevel — 库存缺货状态分析
#include "common.h"

bool run_stocklevel(Ctx &c, Stat *stat, bool measure) {
    int w = c.rnd(1, c.W), d = c.rnd(1, 10);
    std::string r;
    char q[2048];

    auto step = [&](StepId step_id, const char *sql) -> bool {
        if (!timed_send(c, sql, r, stat, measure, step_id)) return false;
        if (is_failure(r)) { timed_abort(c, r, stat, measure); return false; }
        return true;
    };

    if (!timed_send(c, "begin;", r, stat, measure, STEP_BEGIN) || is_failure(r)) return false;

    snprintf(q, sizeof(q), "select d_next_o_id from district where d_w_id=%d and d_id=%d;", w, d);
    if (!step(SL_SELECT_DISTRICT, q)) return false;
    bool has;
    long nid = parse_cell_int(r, has);
    long lo = has && nid > 20 ? nid - 20 : 1;
    int level = c.rnd(10, 20);

    snprintf(q, sizeof(q),
             "select ol_i_id from order_line where ol_w_id=%d and ol_d_id=%d and ol_o_id<%ld and ol_o_id>=%ld;",
             w, d, nid, lo);
    if (!step(SL_SELECT_ORDER_LINE, q)) return false;

    std::vector<int> item_ids = parse_first_col_ints(r, 20);
    std::vector<int> unique_items;
    for (int iid : item_ids) {
        if (std::find(unique_items.begin(), unique_items.end(), iid) == unique_items.end())
            unique_items.push_back(iid);
    }

    for (int iid : unique_items) {
        snprintf(q, sizeof(q),
                 "select count(*) from stock where s_w_id=%d and s_i_id=%d and s_quantity<%d;", w, iid, level);
        if (!step(SL_COUNT_STOCK, q)) return false;
    }

    if (!timed_send(c, "commit;", r, stat, measure, STEP_COMMIT) || is_failure(r)) return false;
    return true;
}
