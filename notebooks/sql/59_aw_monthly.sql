, months AS (
    SELECT unnest(generate_series(date_trunc('month', start_date), date_trunc('month', end_date), INTERVAL '1 month'))::DATE AS month
    FROM bounds
), c AS (
    SELECT date_trunc('month', order_date)::DATE AS month,
           sum(net_sales) AS net_sales, aw_known_sum(gross_contribution) AS contribution,
           count(*) AS orders,
           coalesce(sum(net_sales) FILTER (WHERE channel = 'Online'), 0) AS online_sales,
           coalesce(sum(net_sales) FILTER (WHERE channel = 'Sales-assisted'), 0) AS assisted_sales
    FROM current_orders GROUP BY 1
), p AS (
    SELECT month(order_date) AS month_number, sum(net_sales) AS net_sales
    FROM prior_orders GROUP BY 1
)
SELECT m.month, coalesce(c.net_sales, 0) AS net_sales,
       CASE WHEN b.comparable THEN coalesce(p.net_sales, 0) END AS prior_sales,
       CASE WHEN b.comparable THEN coalesce(c.net_sales, 0) - coalesce(p.net_sales, 0) END AS sales_change,
       coalesce(c.orders, 0) AS orders, c.contribution / nullif(c.net_sales, 0) AS margin,
       coalesce(c.online_sales, 0) AS online_sales, coalesce(c.assisted_sales, 0) AS assisted_sales
FROM months m LEFT JOIN c USING (month) LEFT JOIN p ON p.month_number = month(m.month)
CROSS JOIN bounds b ORDER BY m.month
