, c AS (
    SELECT territory_id, any_value(territory) AS territory, any_value(region) AS region, any_value(country) AS country,
           sum(net_sales) AS net_sales, count(*) AS orders, count(DISTINCT customer_id) AS customers,
           aw_known_sum(gross_contribution) AS contribution
    FROM current_orders GROUP BY territory_id
), p AS (
    SELECT territory_id, any_value(territory) AS territory, any_value(region) AS region, any_value(country) AS country,
           sum(net_sales) AS net_sales FROM prior_orders GROUP BY territory_id
)
SELECT coalesce(c.region, p.region) AS region, coalesce(c.territory, p.territory) AS territory,
       coalesce(c.country, p.country) AS country, coalesce(c.net_sales, 0) AS net_sales,
       CASE WHEN b.comparable THEN coalesce(p.net_sales, 0) END AS prior_sales,
       CASE WHEN b.comparable AND p.net_sales > 0 THEN coalesce(c.net_sales, 0) / p.net_sales - 1 END AS growth,
       c.contribution / nullif(c.net_sales, 0) AS margin,
       coalesce(c.orders, 0) AS orders, coalesce(c.customers, 0) AS customers
FROM c FULL OUTER JOIN p USING (territory_id) CROSS JOIN bounds b
ORDER BY region, net_sales DESC, territory
