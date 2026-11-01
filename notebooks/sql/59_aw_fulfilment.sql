SELECT ship_method, channel, count(*) AS orders,
       count(ship_date) AS dispatched_orders,
       median(dispatch_days) AS median_days, quantile_cont(dispatch_days, 0.9) AS p90_days,
       count(*) FILTER (WHERE ship_date <= due_date)::DOUBLE / nullif(count(ship_date), 0) AS dispatched_by_due,
       sum(freight) / nullif(sum(net_sales), 0) AS freight_ratio,
       sum(net_sales) AS net_sales
FROM current_orders GROUP BY ALL ORDER BY orders DESC, ship_method, channel
