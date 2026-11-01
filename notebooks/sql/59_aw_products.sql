, c AS (
    SELECT category, subcategory, sum(net_sales) AS net_sales, sum(units) AS units,
           aw_known_sum(gross_contribution) AS contribution, sum(discount_value) AS discounts,
           count(DISTINCT product_id) AS products
    FROM current_lines GROUP BY ALL
), p AS (
    SELECT category, subcategory, sum(net_sales) AS net_sales FROM prior_lines GROUP BY ALL
), keys AS (
    SELECT category, subcategory FROM c UNION SELECT category, subcategory FROM p
), months AS (
    SELECT unnest(generate_series(date_trunc('month', start_date), date_trunc('month', end_date), INTERVAL '1 month'))::DATE AS month
    FROM bounds
), monthly AS (
    SELECT category, subcategory, date_trunc('month', order_date)::DATE AS month, sum(net_sales) AS sales
    FROM current_lines GROUP BY ALL
), trends AS (
    SELECT k.category, k.subcategory,
           list(struct_pack(date := m.month, value := coalesce(s.sales, 0)) ORDER BY m.month) AS monthly_sales
    FROM keys k CROSS JOIN months m LEFT JOIN monthly s USING (category, subcategory, month)
    GROUP BY k.category, k.subcategory
)
SELECT k.category, k.subcategory, coalesce(c.net_sales, 0) AS net_sales,
       CASE WHEN b.comparable THEN coalesce(p.net_sales, 0) END AS prior_sales,
       coalesce(c.net_sales, 0) / nullif((SELECT sum(net_sales) FROM c), 0) AS sales_share,
       c.contribution / nullif(c.net_sales, 0) AS margin,
       coalesce(c.units, 0) AS units, coalesce(c.products, 0) AS products,
       c.discounts / nullif(c.net_sales + c.discounts, 0) AS discount_rate, t.monthly_sales
FROM keys k LEFT JOIN c USING (category, subcategory) LEFT JOIN p USING (category, subcategory)
JOIN trends t USING (category, subcategory) CROSS JOIN bounds b
ORDER BY k.category, net_sales DESC, k.subcategory
