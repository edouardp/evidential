-- Normalized local CUR product. Keep missing tags as NULL for selectable missing categories.
SELECT
    billing_month,
    usage_date,
    identity_line_item_id AS line_item_id,
    coalesce(nullif(trim(product_servicecode), ''),
             nullif(trim(line_item_product_code), ''), 'Unspecified') AS service,
    nullif(trim(line_item_usage_type), '') AS usage_type,
    nullif(trim(product_region), '') AS region,
    nullif(trim(line_item_usage_account_id), '') AS account,
    nullif(trim(line_item_line_item_type), '') AS charge_type,
    nullif(trim(resource_tags_user_environment), '') AS environment,
    nullif(trim(resource_tags_user_workload), '') AS workload,
    nullif(trim(resource_tags_user_cost_center), '') AS cost_center,
    nullif(trim(line_item_resource_id), '') AS resource,
    line_item_line_item_description AS description,
    pricing_unit AS unit,
    line_item_usage_amount AS quantity,
    line_item_currency_code AS currency,
    line_item_unblended_cost AS unblended_cost,
    pricing_public_on_demand_cost AS list_cost,
    -- Match aws-cur-example's build.py definition, including retained fee rows.
    CASE WHEN line_item_line_item_type = 'DiscountedUsage'
         THEN reservation_effective_cost
         ELSE line_item_unblended_cost END AS amortized_cost
FROM cur_source
