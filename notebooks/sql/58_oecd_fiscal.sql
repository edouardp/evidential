-- One public-finance series per country/year/measure, normalized for pct format.
SELECT ref_area AS country_code, year,
       CASE measure WHEN 'GGD' THEN 'debt_ratio' ELSE 'fiscal_ratio' END AS metric,
       CASE WHEN isfinite(obs_value) THEN obs_value * multiplier / 100.0 ELSE NULL END AS value,
       coalesce(obs_status_label, obs_status) AS status
FROM oecd_gov_finance
WHERE freq = 'A' AND sector = 'S13' AND category = 'PF' AND edition = 'YU'
  AND unit_measure = 'PT_B1GQ' AND measure IN ('GGD', 'GNLB')
