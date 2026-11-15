# Data Dictionary

## Bronze — `lh_bronze`

### Files/taxi/yellow/yellow_tripdata_YYYY-MM.parquet
Raw NYC TLC yellow taxi trip records, one file per month (source schema, unchanged).

### Files/taxi/reference/taxi_zone_lookup.csv
| Column | Description |
|---|---|
| LocationID | TLC taxi zone id (1–265) |
| Borough | NYC borough name |
| Zone | Zone name |
| service_zone | Yellow Zone / Boro Zone / Airports / EWR |

### bronze_openaq_hourly
| Column | Type | Description |
|---|---|---|
| location_id | bigint | OpenAQ location id |
| location_name | string | Monitoring station name |
| latitude, longitude | double | Station coordinates |
| sensor_id | bigint | OpenAQ sensor id |
| parameter | string | Pollutant (`pm25`, `no2`, `o3`) |
| units | string | Source unit (`µg/m³`, `ppm`) |
| datetime_utc | string | Hour start, UTC ISO-8601 |
| datetime_local | string | Hour start, local time with offset |
| value | double | Hourly average value |
| ingested_at | timestamp | Dataflow load time |

### bronze_worldbank_gdp
| Column | Type | Description |
|---|---|---|
| country_code | string | ISO-3 code (`USA`, `EUU`, `WLD`, …) |
| country_name | string | Country / aggregate name |
| indicator_code | string | `NY.GDP.MKTP.CD` |
| year | bigint | Year |
| gdp_usd | double | GDP, current USD |
| ingested_at | timestamp | Dataflow load time |

### bronze_ecb_fx
| Column | Type | Description |
|---|---|---|
| time_period | date | Business day |
| obs_value | double | USD per 1 EUR (ECB reference rate) |
| currency, currency_denom | string | `USD`, `EUR` |
| ingested_at | timestamp | Dataflow load time |

## Silver — `lh_silver`

### silver_taxi_trips (partitioned by pickup_year, pickup_month)
| Column | Type | Description |
|---|---|---|
| vendor_id | int | TPEP provider |
| pickup_ts, dropoff_ts | timestamp | Trip start / end (local NYC time) |
| passenger_count | int | Passengers (nullable) |
| trip_distance | double | Miles, 0.1–200 |
| pickup_zone_id, dropoff_zone_id | int | TLC zone ids |
| payment_type | int | 1=Credit, 2=Cash, 3=No charge, 4=Dispute |
| fare_amount, tip_amount, total_amount | double | USD |
| pickup_date | date | Trip date |
| pickup_hour | int | 0–23 |
| duration_min | double | 1–240 minutes |
| is_weekend | boolean | Saturday/Sunday |
| time_of_day | string | `morning_rush` 6–9, `midday` 10–15, `evening_rush` 16–19, `night` |

Quality rules: inside analysis window, valid duration/distance, non-negative fare, positive total, deduplicated.

### silver_taxi_zones
`zone_id`, `borough`, `zone_name`, `service_zone` — empty/`N/A` values normalized to `Unknown`.

### silver_air_quality (partitioned by parameter)
| Column | Type | Description |
|---|---|---|
| sensor_id, location_id | bigint | OpenAQ ids |
| location_name, latitude, longitude | | Station metadata |
| borough | string | Nearest borough centroid |
| parameter | string | `pm25`, `no2`, `o3` |
| units | string | Standardized: PM2.5 µg/m³, NO2/O3 ppb |
| value | double | Converted value |
| measured_at | timestamp | Local hour start |
| measure_date, measure_hour | date, int | Time attributes |

Quality rules: inside NYC bounding box, non-negative, unit conversion (ppm×1000, µg/m³→ppb), deduplicated per sensor-hour.

### silver_fx_rates
`rate_date`, `usd_per_eur`, `eur_per_usd` (= 1 / usd_per_eur).

### silver_gdp
`country_code`, `country_name`, `year_number`, `gdp_usd` — nulls removed.

## Gold — `lh_gold` and Warehouse `wh_urban_analytics.gold`

| Lakehouse table | Warehouse table | Grain |
|---|---|---|
| dim_date | DimDate | 1 row per calendar day |
| dim_borough | DimBorough | 1 row per borough |
| dim_zone | DimZone | 1 row per TLC zone |
| dim_fx | DimFX | 1 row per day (weekends forward-filled) |
| dim_gdp | DimGDP | 1 row per country × year |
| fact_taxi_daily | FactTaxiDaily | day × pickup zone |
| fact_air_quality_daily | FactAirQualityDaily | day × borough × pollutant |
| fact_mobility_air_hourly | FactMobilityAirHourly | day × hour × borough |

### FactTaxiDaily
| Column | Description |
|---|---|
| date_key | FK → DimDate (yyyyMMdd) |
| zone_key | FK → DimZone |
| trip_count | Number of trips |
| passenger_count | Sum of passengers |
| distance_miles | Sum of distance |
| fare_usd, tip_usd, revenue_usd | Sums in USD (revenue = total_amount) |
| revenue_eur | revenue_usd × eur_per_usd of that day |
| avg_duration_min | Average trip duration |

### FactAirQualityDaily
`date_key`, `borough_key`, `parameter`, `units`, `avg_value`, `min_value`, `max_value`, `reading_count`, `sensor_count`.

### FactMobilityAirHourly
`date_key`, `hour_of_day`, `time_of_day`, `borough_key`, `trip_count`, `revenue_usd`, `pm25_avg`, `no2_avg`, `o3_avg`.

### DimGDP
`country_code`, `country_name`, `year_number`, `gdp_usd`, `gdp_growth_pct` (YoY %).

### Analytics views
| View | Purpose |
|---|---|
| vw_DailyCityMobilityAir | City-level daily trips vs pollutant |
| vw_MobilityAirPairs | Long-format (trips, pollutant) pairs per analysis segment |
| vw_MobilityAirCorrelation | Pearson r per segment (daily by year, hourly by borough × time of day) |
| vw_MonthlyRevenueUsdEur | Revenue per trip USD vs EUR and average FX |
| vw_YearlyMobilityEconomyEnvironment | Yearly trips, revenue, PM2.5/NO2, USA GDP and growth |
