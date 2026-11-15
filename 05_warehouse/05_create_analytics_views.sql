CREATE VIEW gold.vw_DailyCityMobilityAir
AS
WITH daily_trips AS (
    SELECT date_key, SUM(trip_count) AS trip_count, SUM(revenue_usd) AS revenue_usd
    FROM gold.FactTaxiDaily
    GROUP BY date_key
),
daily_air AS (
    SELECT date_key, parameter, AVG(avg_value) AS avg_value
    FROM gold.FactAirQualityDaily
    GROUP BY date_key, parameter
)
SELECT
    d.calendar_date,
    d.year_number,
    d.month_number,
    d.is_weekend,
    a.parameter AS pollutant,
    CAST(t.trip_count AS FLOAT) AS trips,
    a.avg_value AS pollutant_value
FROM daily_trips AS t
JOIN daily_air AS a ON a.date_key = t.date_key
JOIN gold.DimDate AS d ON d.date_key = t.date_key;
GO

CREATE VIEW gold.vw_MobilityAirPairs
AS
SELECT
    'daily_city' AS analysis_level,
    CAST(year_number AS VARCHAR(50)) AS segment,
    pollutant,
    trips,
    pollutant_value
FROM gold.vw_DailyCityMobilityAir
UNION ALL
SELECT
    'hourly_borough' AS analysis_level,
    CAST(CONCAT(b.borough, ' | ', h.time_of_day) AS VARCHAR(50)) AS segment,
    p.pollutant,
    CAST(h.trip_count AS FLOAT) AS trips,
    p.pollutant_value
FROM gold.FactMobilityAirHourly AS h
JOIN gold.DimBorough AS b ON b.borough_key = h.borough_key
CROSS APPLY (VALUES ('pm25', h.pm25_avg), ('no2', h.no2_avg), ('o3', h.o3_avg)) AS p (pollutant, pollutant_value);
GO

CREATE VIEW gold.vw_MobilityAirCorrelation
AS
SELECT
    analysis_level,
    segment,
    pollutant,
    COUNT(*) AS sample_size,
    (COUNT(*) * SUM(trips * pollutant_value) - SUM(trips) * SUM(pollutant_value))
        / NULLIF(
            SQRT(COUNT(*) * SUM(trips * trips) - SQUARE(SUM(trips)))
            * SQRT(COUNT(*) * SUM(pollutant_value * pollutant_value) - SQUARE(SUM(pollutant_value))),
            0
        ) AS pearson_r
FROM gold.vw_MobilityAirPairs
WHERE trips IS NOT NULL AND pollutant_value IS NOT NULL
GROUP BY analysis_level, segment, pollutant;
GO

CREATE VIEW gold.vw_MonthlyRevenueUsdEur
AS
SELECT
    d.year_number,
    d.month_number,
    SUM(f.trip_count) AS trip_count,
    SUM(f.revenue_usd) AS revenue_usd,
    SUM(f.revenue_eur) AS revenue_eur,
    SUM(f.revenue_usd) / NULLIF(SUM(f.trip_count), 0) AS revenue_per_trip_usd,
    SUM(f.revenue_eur) / NULLIF(SUM(f.trip_count), 0) AS revenue_per_trip_eur,
    AVG(x.usd_per_eur) AS avg_usd_per_eur
FROM gold.FactTaxiDaily AS f
JOIN gold.DimDate AS d ON d.date_key = f.date_key
JOIN gold.DimFX AS x ON x.date_key = f.date_key
GROUP BY d.year_number, d.month_number;
GO

CREATE VIEW gold.vw_YearlyMobilityEconomyEnvironment
AS
WITH yearly_taxi AS (
    SELECT d.year_number, SUM(f.trip_count) AS trip_count, SUM(f.revenue_usd) AS revenue_usd
    FROM gold.FactTaxiDaily AS f
    JOIN gold.DimDate AS d ON d.date_key = f.date_key
    GROUP BY d.year_number
),
yearly_air AS (
    SELECT
        d.year_number,
        AVG(CASE WHEN a.parameter = 'pm25' THEN a.avg_value END) AS pm25_avg,
        AVG(CASE WHEN a.parameter = 'no2' THEN a.avg_value END) AS no2_avg
    FROM gold.FactAirQualityDaily AS a
    JOIN gold.DimDate AS d ON d.date_key = a.date_key
    GROUP BY d.year_number
)
SELECT
    t.year_number,
    t.trip_count,
    t.revenue_usd,
    a.pm25_avg,
    a.no2_avg,
    g.gdp_usd AS usa_gdp_usd,
    g.gdp_growth_pct AS usa_gdp_growth_pct,
    100.0 * (t.trip_count - LAG(t.trip_count) OVER (ORDER BY t.year_number))
        / NULLIF(LAG(t.trip_count) OVER (ORDER BY t.year_number), 0) AS trips_growth_pct,
    100.0 * (a.pm25_avg - LAG(a.pm25_avg) OVER (ORDER BY t.year_number))
        / NULLIF(LAG(a.pm25_avg) OVER (ORDER BY t.year_number), 0) AS pm25_change_pct
FROM yearly_taxi AS t
LEFT JOIN yearly_air AS a ON a.year_number = t.year_number
LEFT JOIN gold.DimGDP AS g ON g.year_number = t.year_number AND g.country_code = 'USA';
GO
