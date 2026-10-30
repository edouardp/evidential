-- One comparable real GDP series per economy and quarter; GY and GCM are not G1.
SELECT ref_area AS country_code, coalesce(ref_area_label, ref_area) AS country,
       period_start, time_period, year, quarter,
       CASE WHEN isfinite(obs_value) THEN obs_value ELSE NULL END AS growth_percent,
       obs_status, obs_status_label
FROM oecd_gdp_growth
WHERE freq = 'Q' AND adjustment = 'Y'
  AND transaction = 'B1GQ' AND sector = 'S1' AND counterpart_sector = 'S1'
  AND activity = '_Z' AND expenditure = '_Z' AND instr_asset = '_Z'
  AND unit_measure = 'PC' AND price_base = 'L' AND transformation = 'G1'
  AND table_identifier = 'T0102' AND unit_mult = '0' AND coalesce(conf_status, 'F') = 'F'
