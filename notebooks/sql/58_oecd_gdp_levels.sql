-- Annual current-price GDP; never sum quarterly annualized levels.
SELECT ref_area AS country_code, year, 'gdp_ppp' AS metric,
       CASE WHEN isfinite(obs_value) THEN obs_value * multiplier ELSE NULL END AS value,
       coalesce(obs_status_label, obs_status) AS status
FROM oecd_gdp_quarterly_usd
WHERE freq = 'A' AND adjustment = 'Y'
  AND transaction = 'B1GQ' AND sector = 'S1' AND counterpart_sector = 'S1'
  AND activity = '_Z' AND expenditure = '_Z' AND instr_asset = '_Z'
  AND unit_measure = 'USD_PPP' AND price_base = 'V' AND transformation = 'LA'
  AND table_identifier = 'T0102' AND coalesce(conf_status, 'F') = 'F'
