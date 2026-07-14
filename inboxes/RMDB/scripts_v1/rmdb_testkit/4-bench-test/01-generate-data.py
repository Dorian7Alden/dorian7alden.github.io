#!/usr/bin/env python3
"""
TPC-C 数据生成器
符合 TPC-C 规范要求的数据生成
"""
import random
import argparse
import os
from datetime import datetime, timedelta

# TPC-C 常量
DIST_PER_WARE = 10
CUST_PER_DIST = 3000
ORD_PER_DIST = 3000
FIRST_UNPROCESSED_O_ID = 2101
ITEM_COUNT = 100000
STOCK_PER_WARE = 100000

def make_alpha_string(min_len, max_len):
    """生成随机字母字符串"""
    length = random.randint(min_len, max_len)
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))

def make_number_string(min_len, max_len):
    """生成随机数字字符串"""
    length = random.randint(min_len, max_len)
    return ''.join(random.choices('0123456789', k=length))

def nu_rand(A, x, y):
    """TPC-C NURand 函数"""
    C = random.randint(0, A)
    return ((random.randint(0, A) | random.randint(x, y)) + C) % (y - x + 1) + x

class TPCCDataGenerator:
    def __init__(self, warehouses, out_dir):
        self.warehouses = warehouses
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        random.seed(42)

    def generate_warehouse(self, w_id):
        """生成 warehouse 表数据"""
        name = make_alpha_string(6, 10)
        street_1 = make_alpha_string(10, 20)
        city = make_alpha_string(10, 20)
        state = make_alpha_string(2, 2)
        zip_code = make_number_string(4, 4) + "11111"
        tax = random.uniform(0, 0.2)
        ytd = 300000.00
        return f"{w_id},{name},{street_1},{city},{state},{zip_code},{tax:.4f},{ytd:.2f}\n"

    def generate_district(self, d_id, w_id):
        """生成 district 表数据"""
        name = make_alpha_string(6, 10)
        street_1 = make_alpha_string(10, 20)
        city = make_alpha_string(10, 20)
        state = make_alpha_string(2, 2)
        zip_code = make_number_string(4, 4) + "11111"
        tax = random.uniform(0, 0.2)
        ytd = 30000.00
        next_o_id = ORD_PER_DIST + 1
        return f"{d_id},{w_id},{name},{street_1},{city},{state},{zip_code},{tax:.4f},{ytd:.2f},{next_o_id}\n"

    def generate_last_name(self, num):
        """根据 TPC-C 规范生成 last name"""
        syllables = ["BAR", "OUGHT", "ABLE", "PRI", "PRES", "ESE", "ANTI", "CALLY", "ATION", "EING"]
        name = syllables[num // 100] + syllables[(num // 10) % 10] + syllables[num % 10]
        return name

    def generate_customer(self, c_id, d_id, w_id):
        """生成 customer 表数据"""
        last = self.generate_last_name(nu_rand(255, 0, 999))
        first = make_alpha_string(8, 16)
        middle = "OE"
        street_1 = make_alpha_string(10, 20)
        city = make_alpha_string(10, 20)
        state = make_alpha_string(2, 2)
        zip_code = make_number_string(4, 4) + "11111"
        phone = make_number_string(16, 16)
        since = datetime.now().strftime("%Y-%m-%d")
        credit = "GC" if random.random() < 0.1 else "BC"
        credit_lim = 50000.00
        discount = random.uniform(0, 0.5)
        balance = -10.00
        ytd_payment = 10.00
        payment_cnt = 1
        delivery_cnt = 0
        data = make_alpha_string(100, 200)
        return f"{c_id},{d_id},{w_id},{first},{middle},{last},{street_1},{city},{state},{zip_code},{phone},{since},{credit},{credit_lim:.2f},{discount:.4f},{balance:.2f},{ytd_payment:.2f},{payment_cnt},{delivery_cnt},{data}\n"

    def generate_item(self, i_id):
        """生成 item 表数据"""
        name = make_alpha_string(14, 24)
        price = random.uniform(1.00, 100.00)
        im_id = random.randint(1, 10000)
        data = make_alpha_string(26, 50)
        if random.random() < 0.1:
            pos = random.randint(0, len(data) - 8)
            data = data[:pos] + "ORIGINAL" + data[pos+8:]
        return f"{i_id},{im_id},{name},{price:.2f},{data}\n"

    def generate_stock(self, s_i_id, w_id):
        """生成 stock 表数据"""
        quantity = random.randint(10, 100)
        dist = [make_alpha_string(24, 24) for _ in range(10)]
        ytd = 0
        order_cnt = 0
        remote_cnt = 0
        data = make_alpha_string(26, 50)
        if random.random() < 0.1:
            pos = random.randint(0, len(data) - 8)
            data = data[:pos] + "ORIGINAL" + data[pos+8:]
        dist_str = ",".join(dist)
        return f"{s_i_id},{w_id},{quantity},{dist_str},{ytd},{order_cnt},{remote_cnt},{data}\n"

    def generate_orders(self, o_id, c_id, d_id, w_id):
        """生成 orders 表数据"""
        entry_d = datetime.now().strftime("%Y-%m-%d")
        carrier_id = random.randint(1, 10) if o_id < FIRST_UNPROCESSED_O_ID else 0
        ol_cnt = random.randint(5, 15)
        all_local = 1
        return f"{o_id},{c_id},{d_id},{w_id},{entry_d},{carrier_id},{ol_cnt},{all_local}\n"

    def generate_new_order(self, o_id, d_id, w_id):
        """生成 new_orders 表数据"""
        return f"{o_id},{d_id},{w_id}\n"

    def generate_order_line(self, o_id, d_id, w_id, ol_number, ol_cnt):
        """生成 order_line 表数据"""
        i_id = random.randint(1, ITEM_COUNT)
        supply_w_id = w_id
        delivery_d = datetime.now().strftime("%Y-%m-%d") if o_id < FIRST_UNPROCESSED_O_ID else ""
        quantity = 5
        amount = 0.0 if o_id >= FIRST_UNPROCESSED_O_ID else random.uniform(0.01, 9999.99)
        dist_info = make_alpha_string(24, 24)
        return f"{o_id},{d_id},{w_id},{ol_number},{i_id},{supply_w_id},{delivery_d},{quantity},{amount:.2f},{dist_info}\n"

    def generate_history(self, c_id, c_d_id, c_w_id, d_id, w_id):
        """生成 history 表数据"""
        date = datetime.now().strftime("%Y-%m-%d")
        amount = 10.00
        data = make_alpha_string(12, 24)
        return f"{c_id},{c_d_id},{c_w_id},{d_id},{w_id},{date},{amount:.2f},{data}\n"

    def generate_all(self):
        """生成所有数据"""
        print(f"生成 TPC-C 数据 (W={self.warehouses}) 到 {self.out_dir}/")
        print(f"  生成 item 表 ({ITEM_COUNT} 行)...")
        with open(f"{self.out_dir}/item.csv", "w") as f:
            f.write("i_id,i_im_id,i_name,i_price,i_data\n")
            for i_id in range(1, ITEM_COUNT + 1):
                f.write(self.generate_item(i_id))
                if i_id % 10000 == 0:
                    print(f"    进度: {i_id}/{ITEM_COUNT}")

        for w_id in range(1, self.warehouses + 1):
            print(f"  生成仓库 {w_id}/{self.warehouses} 数据...")
            with open(f"{self.out_dir}/warehouse.csv", "a" if w_id > 1 else "w") as f:
                if w_id == 1:
                    f.write("w_id,w_name,w_street_1,w_city,w_state,w_zip,w_tax,w_ytd\n")
                f.write(self.generate_warehouse(w_id))
            with open(f"{self.out_dir}/district.csv", "a" if w_id > 1 else "w") as f:
                if w_id == 1:
                    f.write("d_id,d_w_id,d_name,d_street_1,d_city,d_state,d_zip,d_tax,d_ytd,d_next_o_id\n")
                for d_id in range(1, DIST_PER_WARE + 1):
                    f.write(self.generate_district(d_id, w_id))
            with open(f"{self.out_dir}/customer.csv", "a" if w_id > 1 else "w") as f:
                if w_id == 1:
                    f.write("c_id,c_d_id,c_w_id,c_first,c_middle,c_last,c_street_1,c_city,c_state,c_zip,c_phone,c_since,c_credit,c_credit_lim,c_discount,c_balance,c_ytd_payment,c_payment_cnt,c_delivery_cnt,c_data\n")
                for d_id in range(1, DIST_PER_WARE + 1):
                    for c_id in range(1, CUST_PER_DIST + 1):
                        f.write(self.generate_customer(c_id, d_id, w_id))
            with open(f"{self.out_dir}/stock.csv", "a" if w_id > 1 else "w") as f:
                if w_id == 1:
                    f.write("s_i_id,s_w_id,s_quantity,s_dist_01,s_dist_02,s_dist_03,s_dist_04,s_dist_05,s_dist_06,s_dist_07,s_dist_08,s_dist_09,s_dist_10,s_ytd,s_order_cnt,s_remote_cnt,s_data\n")
                for s_i_id in range(1, STOCK_PER_WARE + 1):
                    f.write(self.generate_stock(s_i_id, w_id))
                    if s_i_id % 10000 == 0:
                        print(f"    stock 进度: {s_i_id}/{STOCK_PER_WARE}")
            with open(f"{self.out_dir}/orders.csv", "a" if w_id > 1 else "w") as f_ord, \
                 open(f"{self.out_dir}/new_orders.csv", "a" if w_id > 1 else "w") as f_no, \
                 open(f"{self.out_dir}/order_line.csv", "a" if w_id > 1 else "w") as f_ol:
                if w_id == 1:
                    f_ord.write("o_id,o_c_id,o_d_id,o_w_id,o_entry_d,o_carrier_id,o_ol_cnt,o_all_local\n")
                    f_no.write("no_o_id,no_d_id,no_w_id\n")
                    f_ol.write("ol_o_id,ol_d_id,ol_w_id,ol_number,ol_i_id,ol_supply_w_id,ol_delivery_d,ol_quantity,ol_amount,ol_dist_info\n")
                for d_id in range(1, DIST_PER_WARE + 1):
                    c_ids = list(range(1, CUST_PER_DIST + 1))
                    random.shuffle(c_ids)
                    for o_id in range(1, ORD_PER_DIST + 1):
                        c_id = c_ids[o_id - 1]
                        ol_cnt = random.randint(5, 15)
                        f_ord.write(self.generate_orders(o_id, c_id, d_id, w_id))
                        if o_id >= FIRST_UNPROCESSED_O_ID:
                            f_no.write(self.generate_new_order(o_id, d_id, w_id))
                        for ol_number in range(1, ol_cnt + 1):
                            f_ol.write(self.generate_order_line(o_id, d_id, w_id, ol_number, ol_cnt))
            with open(f"{self.out_dir}/history.csv", "a" if w_id > 1 else "w") as f:
                if w_id == 1:
                    f.write("h_c_id,h_c_d_id,h_c_w_id,h_d_id,h_w_id,h_date,h_amount,h_data\n")
                for d_id in range(1, DIST_PER_WARE + 1):
                    for c_id in range(1, CUST_PER_DIST + 1):
                        f.write(self.generate_history(c_id, d_id, w_id, d_id, w_id))
        print(f"✓ 数据生成完成")

def main():
    parser = argparse.ArgumentParser(description='TPC-C 数据生成器')
    parser.add_argument('--warehouses', '-w', type=int, default=1, help='仓库数量')
    parser.add_argument('--out', '-o', default='./table_data', help='输出目录')
    parser.add_argument('--mini', action='store_true', help='迷你数据集')
    args = parser.parse_args()
    if args.mini:
        global CUST_PER_DIST, ORD_PER_DIST, FIRST_UNPROCESSED_O_ID, ITEM_COUNT, STOCK_PER_WARE
        CUST_PER_DIST = 100
        ORD_PER_DIST = 100
        FIRST_UNPROCESSED_O_ID = 71
        ITEM_COUNT = 1000
        STOCK_PER_WARE = 1000
    generator = TPCCDataGenerator(args.warehouses, args.out)
    generator.generate_all()

if __name__ == '__main__':
    main()
