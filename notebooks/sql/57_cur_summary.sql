SELECT count(*) AS line_items, count(DISTINCT service) AS services,
       count(DISTINCT account) AS accounts,
       coalesce(sum(amortized_cost), 0) AS amortized_cost,
       coalesce(sum(unblended_cost), 0) AS unblended_cost,
       min(usage_date) AS first_day, max(usage_date) AS last_day
FROM cur WHERE /* filters */
