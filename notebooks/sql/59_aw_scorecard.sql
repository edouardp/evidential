, c AS (
    SELECT coalesce(sum(net_sales), 0) AS sales, aw_known_sum(gross_contribution) AS contribution,
           count(*) AS orders, coalesce(sum(units), 0) AS units, count(DISTINCT customer_id) AS customers
    FROM current_orders
), p AS (
    SELECT coalesce(sum(net_sales), 0) AS sales, aw_known_sum(gross_contribution) AS contribution,
           count(*) AS orders, coalesce(sum(units), 0) AS units, count(DISTINCT customer_id) AS customers
    FROM prior_orders
), metrics AS (
    SELECT 1 AS ordinal, 'Net sales' AS metric, c.sales AS current, p.sales AS previous, 'usd0' AS format FROM c, p
    UNION ALL SELECT 2, 'Est. gross contribution', c.contribution, p.contribution, 'usd0' FROM c, p
    UNION ALL SELECT 3, 'Est. contribution margin', c.contribution / nullif(c.sales, 0), p.contribution / nullif(p.sales, 0), 'pct1' FROM c, p
    UNION ALL SELECT 4, 'Orders', c.orders, p.orders, 'num0' FROM c, p
    UNION ALL SELECT 5, 'Units', c.units, p.units, 'num0' FROM c, p
    UNION ALL SELECT 6, 'Active customers', c.customers, p.customers, 'num0' FROM c, p
    UNION ALL SELECT 7, 'Average order value', c.sales / nullif(c.orders, 0), p.sales / nullif(p.orders, 0), 'usd0' FROM c, p
)
SELECT metric, current, CASE WHEN b.comparable THEN previous END AS previous, format,
       CASE WHEN b.comparable THEN CASE WHEN format = 'pct1' THEN (current - previous) * 100
                                       WHEN previous > 0 THEN current / previous - 1 END END AS change,
       CASE WHEN format = 'pct1' THEN '0.0" pp"' ELSE 'pct1' END AS change_format
FROM metrics, bounds b ORDER BY ordinal
