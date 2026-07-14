// TPC-C 压测驱动 — 公共声明
#pragma once
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <string>
#include <thread>
#include <vector>

// ---- 事务类型 ----
enum TxnType { NEW_ORDER = 0, PAYMENT, ORDER_STATUS, DELIVERY, STOCK_LEVEL, NUM_TXN };
static const char *kTxnName[NUM_TXN] = {"NewOrder", "Payment", "OrderStatus", "Delivery", "StockLevel"};
static const int kWeight[NUM_TXN] = {10, 10, 1, 1, 1};
static const int kWeightSum = 23;

// ---- 阶段控制 ----
enum Phase { WARMUP = 0, MEASURE = 1, STOP = 2 };
extern std::atomic<int> g_phase;
extern std::atomic<long> g_commit[NUM_TXN];
extern std::atomic<long> g_abort[NUM_TXN];
extern std::atomic<int> g_connect_failures;

// ---- SQL Step 标识（每个SQL一条，用于细粒度延迟统计） ----
enum StepId {
    STEP_BEGIN = 0, STEP_COMMIT, STEP_ABORT,
    NO_SELECT_CUST_WARE, NO_SELECT_DISTRICT, NO_UPDATE_DISTRICT,
    NO_INSERT_ORDERS, NO_INSERT_NEW_ORDERS, NO_SELECT_ITEM, NO_SELECT_STOCK,
    NO_UPDATE_STOCK, NO_INSERT_ORDER_LINE,
    PAY_SELECT_WARE_YTD, PAY_UPDATE_WARE, PAY_SELECT_WARE_INFO,
    PAY_SELECT_DIST_YTD, PAY_UPDATE_DIST, PAY_SELECT_DIST_INFO,
    PAY_SELECT_CUSTOMER, PAY_UPDATE_CUSTOMER, PAY_INSERT_HISTORY,
    OS_COUNT_CUSTOMER_LAST, OS_SELECT_CUSTOMER_LAST, OS_SELECT_CUSTOMER_ID,
    OS_SELECT_ORDERS, OS_SELECT_ORDER_LINE,
    DEL_SELECT_NEW_ORDER, DEL_DELETE_NEW_ORDER, DEL_SELECT_ORDER_CUSTOMER,
    DEL_UPDATE_ORDERS, DEL_UPDATE_ORDER_LINE, DEL_SUM_ORDER_LINE,
    DEL_SELECT_CUSTOMER, DEL_UPDATE_CUSTOMER,
    SL_SELECT_DISTRICT, SL_SELECT_ORDER_LINE, SL_COUNT_STOCK,
    NUM_STEPS
};
static const char *kStepName[NUM_STEPS] = {
    "control.begin", "control.commit", "control.abort",
    "NewOrder.select_customer_warehouse", "NewOrder.select_district", "NewOrder.update_district",
    "NewOrder.insert_orders", "NewOrder.insert_new_orders", "NewOrder.select_item", "NewOrder.select_stock",
    "NewOrder.update_stock", "NewOrder.insert_order_line",
    "Payment.select_warehouse_ytd", "Payment.update_warehouse", "Payment.select_warehouse_info",
    "Payment.select_district_ytd", "Payment.update_district", "Payment.select_district_info",
    "Payment.select_customer", "Payment.update_customer", "Payment.insert_history",
    "OrderStatus.count_customer_last", "OrderStatus.select_customer_last", "OrderStatus.select_customer_id",
    "OrderStatus.select_orders", "OrderStatus.select_order_line",
    "Delivery.select_new_orders", "Delivery.delete_new_orders", "Delivery.select_order_customer",
    "Delivery.update_orders", "Delivery.update_order_line", "Delivery.sum_order_line",
    "Delivery.select_customer", "Delivery.update_customer",
    "StockLevel.select_district", "StockLevel.select_order_line", "StockLevel.count_stock"
};

// ---- 统计 ----
struct Stat {
    long commit[NUM_TXN] = {0};
    long abort[NUM_TXN] = {0};
    std::vector<double> lat[NUM_TXN];
    long step_count[NUM_STEPS] = {0};
    std::vector<double> step_lat[NUM_STEPS];
    void merge(const Stat &o) {
        for (int i = 0; i < NUM_TXN; i++) {
            commit[i] += o.commit[i]; abort[i] += o.abort[i];
            lat[i].insert(lat[i].end(), o.lat[i].begin(), o.lat[i].end());
        }
        for (int i = 0; i < NUM_STEPS; i++) {
            step_count[i] += o.step_count[i];
            step_lat[i].insert(step_lat[i].end(), o.step_lat[i].begin(), o.step_lat[i].end());
        }
    }
};

inline double pct(std::vector<double> &v, double p) {
    if (v.empty()) return 0;
    std::sort(v.begin(), v.end());
    size_t idx = (size_t)(p / 100.0 * (v.size() - 1));
    return v[idx];
}

// ---- 上下文 ----
struct Ctx {
    int fd, W, customers_per_dist, orders_per_dist, items;
    std::mt19937_64 rng;
    int rnd(int lo, int hi) { return std::uniform_int_distribution<int>(lo, hi)(rng); }
};

// ---- 网络 ----
inline int connect_server(const char *host, int port) {
    hostent *he = gethostbyname(host);
    if (!he) return -1;
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    sockaddr_in addr{};
    addr.sin_family = AF_INET; addr.sin_port = htons(port);
    addr.sin_addr = *(in_addr *)he->h_addr;
    if (connect(fd, (sockaddr *)&addr, sizeof(addr)) < 0) { close(fd); return -1; }
    int one = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));
    return fd;
}

inline bool send_cmd(int fd, const std::string &sql, std::string &resp) {
    const char *p = sql.c_str();
    size_t left = sql.size() + 1;
    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) { if (errno == EINTR) continue; return false; }
        if (n == 0) return false;
        p += n; left -= (size_t)n;
    }
    resp.clear();
    char buf[65536];
    while (true) {
        ssize_t n = read(fd, buf, sizeof(buf));
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return false;
        for (ssize_t i = 0; i < n; i++) {
            if (buf[i] == '\0') return true;
            resp.push_back(buf[i]);
        }
    }
}

inline bool is_failure(const std::string &r) {
    // 表格输出（以 | 开头）必定是查询成功；数据列可能包含任意字符串
    if (!r.empty() && r[0] == '|') return false;
    return r.compare(0, 5, "abort") == 0 ||
           r.compare(0, 5, "Error") == 0;
}

// ---- 响应解析 ----
inline std::string trim_cell(std::string s) {
    size_t b = 0, e = s.size();
    while (b < e && std::isspace((unsigned char)s[b])) b++;
    while (e > b && std::isspace((unsigned char)s[e - 1])) e--;
    return s.substr(b, e - b);
}

inline bool first_data_row_cells(const std::string &resp, std::vector<std::string> &cells) {
    cells.clear();
    size_t pos = 0; int pipe_lines = 0;
    while (pos < resp.size()) {
        size_t eol = resp.find('\n', pos);
        if (eol == std::string::npos) eol = resp.size();
        if (pos < resp.size() && resp[pos] == '|') {
            pipe_lines++;
            if (pipe_lines == 2) {
                size_t s = pos + 1;
                while (s < eol) {
                    size_t p = resp.find('|', s);
                    if (p == std::string::npos || p > eol) break;
                    cells.push_back(trim_cell(resp.substr(s, p - s)));
                    s = p + 1;
                }
                return !cells.empty();
            }
        }
        pos = eol + 1;
    }
    return false;
}

inline bool parse_cell_int_at(const std::string &resp, size_t idx, long &val) {
    std::vector<std::string> cells;
    if (!first_data_row_cells(resp, cells) || idx >= cells.size()) return false;
    char *end = nullptr;
    long v = std::strtol(cells[idx].c_str(), &end, 10);
    if (end == cells[idx].c_str()) return false;
    val = v; return true;
}

inline bool parse_cell_double_at(const std::string &resp, size_t idx, double &val) {
    std::vector<std::string> cells;
    if (!first_data_row_cells(resp, cells) || idx >= cells.size()) return false;
    char *end = nullptr; errno = 0;
    double v = std::strtod(cells[idx].c_str(), &end);
    if (end == cells[idx].c_str() || errno == ERANGE) return false;
    val = v; return true;
}

inline long parse_cell_int(const std::string &resp, bool &has_row) {
    long val = 0;
    has_row = parse_cell_int_at(resp, 0, val);
    return val;
}

inline double parse_cell_double(const std::string &resp, bool &has_row) {
    double val = 0;
    has_row = parse_cell_double_at(resp, 0, val);
    return val;
}

inline std::vector<int> parse_first_col_ints(const std::string &resp, size_t limit) {
    std::vector<int> vals;
    size_t pos = 0; int pipe_lines = 0;
    while (pos < resp.size() && vals.size() < limit) {
        size_t eol = resp.find('\n', pos);
        if (eol == std::string::npos) eol = resp.size();
        if (pos < resp.size() && resp[pos] == '|') {
            pipe_lines++;
            if (pipe_lines >= 2) {
                size_t s = pos + 1;
                size_t p = resp.find('|', s);
                if (p != std::string::npos && p <= eol) {
                    std::string cell = trim_cell(resp.substr(s, p - s));
                    char *end = nullptr;
                    long v = std::strtol(cell.c_str(), &end, 10);
                    if (end != cell.c_str()) vals.push_back((int)v);
                }
            }
        }
        pos = eol + 1;
    }
    return vals;
}

// ---- 辅助 ----
inline bool timed_send(Ctx &c, const char *sql, std::string &resp, Stat *stat, bool measure, StepId step) {
    auto t0 = std::chrono::steady_clock::now();
    bool ok = send_cmd(c.fd, sql, resp);
    if (measure && stat != nullptr) {
        double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
        stat->step_count[step]++;
        stat->step_lat[step].push_back(ms);
    }
    return ok;
}

inline void timed_abort(Ctx &c, std::string &resp, Stat *stat, bool measure) {
    timed_send(c, "abort;", resp, stat, measure, STEP_ABORT);
}

inline std::string last_name_from_num(int num) {
    static const char *kSyllables[] = {
        "BAR", "OUGHT", "ABLE", "PRI", "PRES", "ESE", "ANTI", "CALLY", "ATION", "EING"
    };
    num %= 1000;
    return std::string(kSyllables[num / 100]) + kSyllables[(num / 10) % 10] + kSyllables[num % 10];
}

inline TxnType pick_txn(Ctx &c) {
    int x = c.rnd(1, kWeightSum), acc = 0;
    for (int i = 0; i < NUM_TXN; i++) {
        acc += kWeight[i];
        if (x <= acc) return (TxnType)i;
    }
    return NEW_ORDER;
}

// ---- 事务函数声明 ----
bool run_neworder(Ctx &c, Stat *stat, bool measure);
bool run_payment(Ctx &c, Stat *stat, bool measure);
bool run_orderstatus(Ctx &c, Stat *stat, bool measure);
bool run_delivery(Ctx &c, Stat *stat, bool measure);
bool run_stocklevel(Ctx &c, Stat *stat, bool measure);

// ---- 进度报告 ----
void progress_reporter(int round, int total_rounds, int warmup_sec, int measure_sec);
