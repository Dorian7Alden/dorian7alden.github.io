// TPC-C 压测驱动 — main, worker, progress
#include "common.h"

std::atomic<int> g_phase{WARMUP};
std::atomic<long> g_commit[NUM_TXN] = {};
std::atomic<long> g_abort[NUM_TXN] = {};
std::atomic<int> g_connect_failures{0};

void worker(const char *host, int port, int W, int customers, int orders, int items, uint64_t seed, Stat *out) {
    Ctx c;
    // 连接重试：避免 server 就绪 race condition 导致 worker 静默失败
    int fd = -1;
    for (int retry = 0; retry < 10; retry++) {
        fd = connect_server(host, port);
        if (fd >= 0) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    c.fd = fd;
    c.W = W;
    c.customers_per_dist = customers;
    c.orders_per_dist = orders;
    c.items = items;
    c.rng.seed(seed);
    if (c.fd < 0) {
        g_connect_failures.fetch_add(1, std::memory_order_relaxed);
        return;
    }
    using clk = std::chrono::steady_clock;
    while (true) {
        int phase_at_start = g_phase.load(std::memory_order_relaxed);
        if (phase_at_start == STOP) break;
        TxnType t = pick_txn(c);
        auto t0 = clk::now();
        bool ok;
        switch (t) {
            case NEW_ORDER:    ok = run_neworder(c, out, phase_at_start == MEASURE); break;
            case PAYMENT:      ok = run_payment(c, out, phase_at_start == MEASURE); break;
            case ORDER_STATUS: ok = run_orderstatus(c, out, phase_at_start == MEASURE); break;
            case DELIVERY:     ok = run_delivery(c, out, phase_at_start == MEASURE); break;
            default:           ok = run_stocklevel(c, out, phase_at_start == MEASURE); break;
        }
        double ms = std::chrono::duration<double, std::milli>(clk::now() - t0).count();
        if (ok) g_commit[t].fetch_add(1, std::memory_order_relaxed);
        else    g_abort[t].fetch_add(1, std::memory_order_relaxed);
        if (phase_at_start == MEASURE) {
            if (ok) { out->commit[t]++; out->lat[t].push_back(ms); }
            else out->abort[t]++;
        }
    }
    close(c.fd);
}

void progress_reporter(int round, int total_rounds, int warmup_sec, int measure_sec) {
    auto round_start = std::chrono::steady_clock::now();
    auto measure_start_time = round_start;
    bool measure_started = false;
    long snap_commit[NUM_TXN] = {0}, snap_abort[NUM_TXN] = {0};
    const int warmup_interval = 5, measure_interval = 15;
    long last_warmup_print = -warmup_interval, last_measure_print = -measure_interval;

    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        int phase = g_phase.load(std::memory_order_relaxed);
        if (phase == STOP) break;

        auto now = std::chrono::steady_clock::now();
        long round_elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - round_start).count();

        long cur_c[NUM_TXN], cur_a[NUM_TXN];
        long tot_c = 0, tot_a = 0;
        for (int i = 0; i < NUM_TXN; i++) {
            cur_c[i] = g_commit[i].load(std::memory_order_relaxed);
            cur_a[i] = g_abort[i].load(std::memory_order_relaxed);
            tot_c += cur_c[i]; tot_a += cur_a[i];
        }

        if (phase == WARMUP) {
            if (round_elapsed - last_warmup_print >= warmup_interval || round_elapsed >= warmup_sec) {
                last_warmup_print = round_elapsed;
                long display_elapsed = std::min(round_elapsed, (long)warmup_sec);
                double tpmc = display_elapsed > 0 ? cur_c[NEW_ORDER] / (display_elapsed / 60.0) : 0;
                fprintf(stderr, "[Round %d/%d] warmup %3ld/%ds | tpmC=%8.1f total_txn=%8ld abort=%4.1f%%\n",
                        round, total_rounds, display_elapsed, warmup_sec,
                        tpmc, tot_c, tot_c + tot_a ? 100.0 * tot_a / (tot_c + tot_a) : 0.0);
            }
        } else if (phase == MEASURE) {
            if (!measure_started) {
                measure_started = true;
                measure_start_time = now;
                for (int i = 0; i < NUM_TXN; i++) { snap_commit[i] = cur_c[i]; snap_abort[i] = cur_a[i]; }
                last_measure_print = -measure_interval;
            }
            long m_elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - measure_start_time).count();
            if (m_elapsed - last_measure_print >= measure_interval || m_elapsed >= measure_sec) {
                last_measure_print = m_elapsed;
                long display_m = std::min(m_elapsed, (long)measure_sec);
                long dc[NUM_TXN], da[NUM_TXN];
                long tot_dc = 0, tot_da = 0;
                for (int i = 0; i < NUM_TXN; i++) {
                    dc[i] = cur_c[i] - snap_commit[i]; da[i] = cur_a[i] - snap_abort[i];
                    tot_dc += dc[i]; tot_da += da[i];
                }
                double tpmc = display_m > 0 ? dc[NEW_ORDER] / (display_m / 60.0) : 0;
                fprintf(stderr, "[Round %d/%d] measure %3ld/%ds | tpmC=%8.1f total_txn=%8ld abort=%4.1f%%\n",
                        round, total_rounds, display_m, measure_sec,
                        tpmc, tot_dc, tot_dc + tot_da ? 100.0 * tot_da / (tot_dc + tot_da) : 0.0);
            }
        }
    }
}

int main(int argc, char **argv) {
    const char *host = "127.0.0.1";
    int port = 8765, threads = 16, W = 1, warmup = 30, measure = 360, rounds = 3;
    int customers = 3000, orders = 3000, items = 100000;
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() { return std::atoi(argv[++i]); };
        if (a == "-h") host = argv[++i];
        else if (a == "-p") port = next();
        else if (a == "-t") threads = next();
        else if (a == "-w") W = next();
        else if (a == "--warmup") warmup = next();
        else if (a == "--measure") measure = next();
        else if (a == "-r") rounds = next();
        else if (a == "--customers") customers = next();
        else if (a == "--orders") orders = next();
        else if (a == "--items") items = next();
    }
    if (threads <= 0 || W <= 0 || warmup < 0 || measure <= 0 || rounds <= 0 ||
        customers <= 0 || orders <= 0 || items <= 0) {
        fprintf(stderr, "[driver] invalid arguments\n");
        return 1;
    }
    printf("[driver] host=%s port=%d threads=%d W=%d warmup=%ds measure=%ds rounds=%d\n",
           host, port, threads, W, warmup, measure, rounds);
    printf("[driver] scale: customers/dist=%d orders/dist=%d items=%d\n", customers, orders, items);
    printf("[driver] target mix: NewOrder=10/23 Payment=10/23 OrderStatus=1/23 Delivery=1/23 StockLevel=1/23\n");

    int probe = connect_server(host, port);
    if (probe < 0) { fprintf(stderr, "[driver] cannot connect to server\n"); return 1; }
    close(probe);

    std::vector<double> tpmc_rounds;
    double meas_min = measure / 60.0;
    for (int rd = 1; rd <= rounds; rd++) {
        for (int i = 0; i < NUM_TXN; i++) {
            g_commit[i].store(0, std::memory_order_relaxed);
            g_abort[i].store(0, std::memory_order_relaxed);
        }

        std::vector<Stat> stats(threads);
        std::vector<std::thread> ts;
        g_connect_failures.store(0, std::memory_order_relaxed);
        g_phase.store(WARMUP);
        for (int i = 0; i < threads; i++)
            ts.emplace_back(worker, host, port, W, customers, orders, items,
                            0x9e3779b97f4a7c15ULL * (rd * 131 + i + 1), &stats[i]);

        std::thread progress(progress_reporter, rd, rounds, warmup, measure);
        std::this_thread::sleep_for(std::chrono::seconds(warmup));
        g_phase.store(MEASURE);
        std::this_thread::sleep_for(std::chrono::seconds(measure));
        g_phase.store(STOP);

        progress.join();
        for (auto &t : ts) t.join();
        int conn_fail = g_connect_failures.load(std::memory_order_relaxed);
        if (conn_fail > 0) {
            fprintf(stderr, "[driver] %d worker connection(s) failed; result is invalid\n", conn_fail);
            return 2;
        }

        Stat agg;
        for (auto &s : stats) agg.merge(s);
        long tot_commit = 0, tot_abort = 0;
        for (int i = 0; i < NUM_TXN; i++) { tot_commit += agg.commit[i]; tot_abort += agg.abort[i]; }
        double tpmc = agg.commit[NEW_ORDER] / meas_min;
        tpmc_rounds.push_back(tpmc);

        printf("\n===== Round %d =====\n", rd);
        printf("tpmC (NewOrder committed/min) = %.2f\n", tpmc);
        printf("total throughput = %.2f txn/min | abort rate = %.2f%%\n",
               tot_commit / meas_min,
               tot_commit + tot_abort ? 100.0 * tot_abort / (tot_commit + tot_abort) : 0.0);
        printf("%-12s %10s %8s %9s %10s %10s\n", "txn", "commit", "abort", "mix(%)", "p50(ms)", "p99(ms)");
        for (int i = 0; i < NUM_TXN; i++)
            printf("%-12s %10ld %8ld %9.2f %10.2f %10.2f\n", kTxnName[i], agg.commit[i], agg.abort[i],
                   tot_commit + tot_abort ? 100.0 * (agg.commit[i] + agg.abort[i]) / (tot_commit + tot_abort) : 0.0,
                   pct(agg.lat[i], 50), pct(agg.lat[i], 99));

        printf("\n%-38s %10s %10s %10s\n", "step", "count", "p50(ms)", "p99(ms)");
        for (int i = 0; i < NUM_STEPS; i++) {
            if (agg.step_count[i] == 0) continue;
            printf("%-38s %10ld %10.2f %10.2f\n", kStepName[i], agg.step_count[i],
                   pct(agg.step_lat[i], 50), pct(agg.step_lat[i], 99));
        }
    }

    std::sort(tpmc_rounds.begin(), tpmc_rounds.end());
    double median = tpmc_rounds[tpmc_rounds.size() / 2];
    if (tpmc_rounds.size() % 2 == 0)
        median = (tpmc_rounds[tpmc_rounds.size() / 2 - 1] + tpmc_rounds[tpmc_rounds.size() / 2]) / 2.0;
    printf("\n========================================\n");
    printf("FINAL tpmC (median of %d rounds) = %.2f\n", rounds, median);
    printf("========================================\n");
    return 0;
}
