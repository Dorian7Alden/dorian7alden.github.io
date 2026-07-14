# 决赛性能测试SQL示例

## new_order：读写事务

客户输⼊⼀笔新的订单交易

```sql
select c_discount, c_last, c_credit, w_tax from customer, warehouse where w_id=:w_id and c_w_id=w_id and c_d_id=:d_id and c_id=:c_id;
select d_next_o_id, d_tax from district where d_id=:d_id and d_w_id=:d_w_id;
update district set d_next_o_id=:d_next_o_id where d_id=:d_id and d_w_id=:w_id;
insert into orders values(:o_id, :o_d_id, :o_w_id, :o_c_id, :o_entry_d, :o_carrier_id, :o_ol_cnt, :o_all_local);
insert into new_orders values(:o_id, :d_id, :w_id);
select i_price, i_name, i_data from item where i_id=:ol_i_id;
select s_quantity, s_data, s_dist_01, s_dist_02, s_dist_03, s_dist_04, s_dist_05, s_dist_06, s_dist_07, s_dist_08, s_dist_09, s_dist_10 from stock where s_i_id=:ol_i_id and s_w_id = :ol_supply_w_id;
UPDATE stock SET s_quantity=:s_quantity where s_i_id = :ol_i_id and s_w_id = :ol_supply_w_id;
insert into order_line values (:ol_o_id, :ol_d_id, :ol_w_id, :ol_number, :ol_i_id, :ol_supply_w_id, :ol_delivery_d, :ol_quantity, :ol_amount, :ol_dist_info);
```

## payment：读写事务

更新客户账户余额

```sql
update warehouse set w_ytd=w_ytd+:h_amount where w_id=:w_id;
select w_street_1, w_street_2, w_city, w_state, w_zip, w_name from warehouse where w_id=:w_id;
update district set d_ytd=d_ytd+:h_amount where d_w_id=:w_id and d_id=:d_id;
select d_street_1, d_street_2, d_city, d_state, d_zip, d_name from district where d_w_id=:w_id and d_id=:d_id;
select c_first, c_middle, c_last, c_street_1, c_street_2, c_city, c_state, c_zip, c_phone, c_credit, c_credit_lim, c_discount, c_balance, c_since from customer where c_w_id=:w_id and c_d_id=:d_id and c_id=:c_id;
update customer set c_balance=:c_balance where c_w_id=:w_id and c_d_id=:d_id and c_id=:c_id;
insert into history values(:h_c_id, :h_c_d_id, :h_c_w_id, :h_d_id, :h_w_id, :h_date, :h_amount, :h_data);
```

## delivery：读写事务

发货

```sql
select min(no_o_id) as min_o_id from new_orders where no_d_id=:d_id and no_w_id=:w_id;
delete from new_orders where no_o_id=:o_id and no_d_id=:d_id and no_w_id=:w_id;
select o_c_id from orders where o_id=:no_o_id and o_d_id=:d_id and o_w_id=:w_id;
update orders set o_carrier_id=:o_carrier_id where o_id=:no_o_id and o_d_id=:d_id and o_w_id=:w_id;
update order_line set ol_delivery_d=:datetime where ol_o_id=:no_o_id and ol_d_id=:d_id and ol_w_id=:w_id;
select sum(ol_amount) as sum_amount from order_line where ol_o_id=:no_o_id and ol_d_id=:d_id;
update customer set c_balance=:c_balance, c_delivery_cnt=c_delivery_cnt+1 where c_id=:c_id and c_d_id=:d_id and c_w_id=:w_id;
```

## order_status：只读事务

查询客户最近的交易状态

```sql
select count(c_id) as count_c_id from customer where c_w_id=:c_w_id and c_d_id=:c_d_id and c_last=:c_last;
select c_balance, c_first, c_middle, c_last from customer where c_w_id=:c_w_id and c_d_id=:c_d_id and c_last=:c_last order by c_fisrt;
/* 60%执⾏上述两条，40%执⾏下述⼀条 */
select c_balance, c_first, c_middle, c_last from customer where c_w_id=:c_w_id and c_d_id=:c_d_id and c_id=:c_id;
select o_id, o_entry_d, o_carrier_id from orders where o_w_id=:c_w_id and o_d_id=:c_d_id and o_c_id=:c_id and o_id=:o_id;
select ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_delivery_d from order_line where ol_w_id=:c_w_id and ol_d_id=:c_d_id and ol_o_id=:o_id;
```

## stock-level：只读事务

查询仓库库存状况

```sql
select d_next_o_id from district where d_id=:d_id and d_w_id=:w_id;
select ol_i_id from order_line where ol_w_id=:w_id and ol_d_id=:d_id and ol_o_id<:d_next_o_id and ol_o_id>=(:d_next_o_id-20);
select count(*) as count_stock from stock where s_w_id=:w_id and s_i_id=:ol_i_id and s_quantity<:level;
```
