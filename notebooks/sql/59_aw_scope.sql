WITH bounds AS (
    SELECT $start::DATE AS start_date, $end::DATE AS end_date,
           $prior_start::DATE AS prior_start, $prior_end::DATE AS prior_end,
           $comparable::BOOLEAN AS comparable, $channel::VARCHAR AS channel
), current_orders AS (
    SELECT o.* FROM aw_orders o, bounds b
    WHERE o.order_date BETWEEN b.start_date AND b.end_date
      AND (b.channel = 'All channels' OR o.channel = b.channel)
), prior_orders AS (
    SELECT o.* FROM aw_orders o, bounds b
    WHERE b.comparable AND o.order_date BETWEEN b.prior_start AND b.prior_end
      AND (b.channel = 'All channels' OR o.channel = b.channel)
), current_lines AS (
    SELECT l.* FROM aw_lines l JOIN current_orders o USING (order_id)
), prior_lines AS (
    SELECT l.* FROM aw_lines l JOIN prior_orders o USING (order_id)
)
