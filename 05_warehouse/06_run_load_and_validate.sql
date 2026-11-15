EXEC gold.usp_load_star_schema;

SELECT 'DimDate' AS table_name, COUNT(*) AS row_count FROM gold.DimDate
UNION ALL SELECT 'DimBorough', COUNT(*) FROM gold.DimBorough
UNION ALL SELECT 'DimZone', COUNT(*) FROM gold.DimZone
UNION ALL SELECT 'DimFX', COUNT(*) FROM gold.DimFX
UNION ALL SELECT 'DimGDP', COUNT(*) FROM gold.DimGDP
UNION ALL SELECT 'FactTaxiDaily', COUNT(*) FROM gold.FactTaxiDaily
UNION ALL SELECT 'FactAirQualityDaily', COUNT(*) FROM gold.FactAirQualityDaily
UNION ALL SELECT 'FactMobilityAirHourly', COUNT(*) FROM gold.FactMobilityAirHourly;

SELECT TOP 20 *
FROM gold.vw_MobilityAirCorrelation
WHERE sample_size >= 30
ORDER BY ABS(pearson_r) DESC;

SELECT * FROM gold.vw_MonthlyRevenueUsdEur ORDER BY year_number, month_number;

SELECT * FROM gold.vw_YearlyMobilityEconomyEnvironment ORDER BY year_number;
