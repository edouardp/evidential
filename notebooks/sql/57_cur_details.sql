SELECT usage_date, service, region, usage_type, charge_type, account,
       resource, description, quantity, unit, amortized_cost, unblended_cost, line_item_id
FROM cur WHERE /* filters */
ORDER BY amortized_cost DESC NULLS LAST, usage_date, line_item_id
LIMIT ?
