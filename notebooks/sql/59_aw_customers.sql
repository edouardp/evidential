SELECT CASE WHEN first_seen >= b.start_date THEN 'First observed in period' ELSE 'Previously observed' END AS cohort,
       count(DISTINCT customer_id) AS customers, count(*) AS orders, sum(net_sales) AS net_sales,
       sum(net_sales) / nullif(count(DISTINCT customer_id), 0) AS sales_per_customer,
       count(*)::DOUBLE / nullif(count(DISTINCT customer_id), 0) AS orders_per_customer,
       aw_known_sum(gross_contribution) / nullif(sum(net_sales), 0) AS margin
FROM current_orders JOIN aw_first_seen USING (customer_id) CROSS JOIN bounds b
GROUP BY cohort ORDER BY net_sales DESC
