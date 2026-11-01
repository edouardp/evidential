, c AS (
    SELECT customer_id, any_value(customer) AS customer, any_value(territory) AS territory,
           sum(net_sales) AS net_sales, count(*) AS orders,
           aw_known_sum(gross_contribution) AS contribution
    FROM current_orders WHERE store_id IS NOT NULL GROUP BY customer_id
), p AS (
    SELECT customer_id, any_value(customer) AS customer, any_value(territory) AS territory,
           sum(net_sales) AS net_sales FROM prior_orders WHERE store_id IS NOT NULL GROUP BY customer_id
)
SELECT coalesce(c.customer_id, p.customer_id) AS customer_id, coalesce(c.customer, p.customer) AS customer,
       coalesce(c.territory, p.territory) AS territory, coalesce(c.net_sales, 0) AS net_sales,
       CASE WHEN b.comparable THEN coalesce(p.net_sales, 0) END AS prior_sales,
       coalesce(c.net_sales, 0) / nullif((SELECT sum(net_sales) FROM current_orders), 0) AS company_sales_share,
       c.net_sales / nullif(c.orders, 0) AS average_order, coalesce(c.orders, 0) AS orders,
       c.contribution / nullif(c.net_sales, 0) AS margin
FROM c FULL OUTER JOIN p USING (customer_id) CROSS JOIN bounds b
ORDER BY net_sales DESC, customer_id
LIMIT 15
