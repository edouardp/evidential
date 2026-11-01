SELECT country_code, any_value(country) AS country, sum(net_sales) AS net_sales, count(*) AS orders
FROM current_orders GROUP BY country_code ORDER BY net_sales DESC
