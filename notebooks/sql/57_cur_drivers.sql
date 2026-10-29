-- Aggregate only quantities with identical units; filter before every aggregation.
WITH matching AS (
    SELECT * FROM cur WHERE /* filters */
), daily AS (
    SELECT service, usage_type, region, charge_type, unit, usage_date,
           sum(amortized_cost) AS cost, sum(unblended_cost) AS unblended_cost,
           sum(quantity) AS quantity, count(*) AS line_items
    FROM matching GROUP BY ALL
), calendar AS (
    SELECT unnest(generate_series(min(usage_date), max(usage_date), INTERVAL 1 DAY))::DATE AS day
    FROM matching
), drivers AS (
    SELECT service, usage_type, region, charge_type, unit,
           sum(cost) AS amortized_cost, sum(unblended_cost) AS unblended_cost,
           sum(quantity) AS quantity, sum(line_items)::BIGINT AS line_items
    FROM daily GROUP BY ALL
), trends AS (
    SELECT drivers.service, drivers.usage_type, drivers.region, drivers.charge_type, drivers.unit,
           list(struct_pack(date := calendar.day, value := coalesce(daily.cost, 0)) ORDER BY calendar.day) AS daily_cost
    FROM drivers CROSS JOIN calendar
    LEFT JOIN daily ON daily.service = drivers.service
        AND daily.usage_type IS NOT DISTINCT FROM drivers.usage_type
        AND daily.region IS NOT DISTINCT FROM drivers.region
        AND daily.charge_type IS NOT DISTINCT FROM drivers.charge_type
        AND daily.unit IS NOT DISTINCT FROM drivers.unit
        AND daily.usage_date = calendar.day
    GROUP BY ALL
)
SELECT drivers.*, drivers.amortized_cost / nullif((SELECT sum(amortized_cost) FROM matching), 0) AS share,
       trends.daily_cost
FROM drivers JOIN trends ON trends.service = drivers.service
    AND trends.usage_type IS NOT DISTINCT FROM drivers.usage_type
    AND trends.region IS NOT DISTINCT FROM drivers.region
    AND trends.charge_type IS NOT DISTINCT FROM drivers.charge_type
    AND trends.unit IS NOT DISTINCT FROM drivers.unit
ORDER BY amortized_cost DESC NULLS LAST, service, usage_type, region, charge_type, unit
