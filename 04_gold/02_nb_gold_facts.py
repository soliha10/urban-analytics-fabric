# %%
%run nb_common

# %%
HOURLY_KEYS = ["event_date", "hour_of_day", "borough_key"]


def silver(table):
    return read_table(SILVER_LAKEHOUSE, table)


def gold(table):
    return read_table(GOLD_LAKEHOUSE, table)


def with_borough_key(df):
    return df.join(gold("dim_borough"), "borough")


# %%
def taxi_daily_metrics():
    return [
        F.count("*").alias("trip_count"),
        F.sum("passenger_count").alias("passenger_count"),
        rounded_sum("trip_distance", "distance_miles"),
        rounded_sum("fare_amount", "fare_usd"),
        rounded_sum("tip_amount", "tip_usd"),
        rounded_sum("total_amount", "revenue_usd"),
        F.round(F.avg("duration_min"), 2).alias("avg_duration_min"),
    ]


def with_revenue_eur(daily):
    rates = gold("dim_fx").select("date_key", "eur_per_usd")
    converted = daily.join(rates, "date_key", "left")
    return converted.withColumn("revenue_eur", F.round(F.col("revenue_usd") * F.col("eur_per_usd"), 2)).drop("eur_per_usd")


def build_fact_taxi_daily():
    trips = silver("silver_taxi_trips").withColumnRenamed("pickup_zone_id", "zone_key")
    daily = trips.groupBy("pickup_date", "zone_key").agg(*taxi_daily_metrics())
    return with_revenue_eur(with_date_key(daily, "pickup_date").drop("pickup_date"))


# %%
def air_daily_metrics():
    return [
        F.round(F.avg("value"), 3).alias("avg_value"),
        F.round(F.min("value"), 3).alias("min_value"),
        F.round(F.max("value"), 3).alias("max_value"),
        F.count("*").alias("reading_count"),
        F.countDistinct("sensor_id").alias("sensor_count"),
    ]


def build_fact_air_quality_daily():
    air = with_borough_key(silver("silver_air_quality"))
    daily = air.groupBy("measure_date", "borough_key", "parameter", "units").agg(*air_daily_metrics())
    return with_date_key(daily, "measure_date").drop("measure_date")


# %%
def taxi_hourly_by_borough():
    zones = gold("dim_zone").select(F.col("zone_key").alias("pickup_zone_id"), "borough_key")
    trips = silver("silver_taxi_trips").join(zones, "pickup_zone_id")
    hourly = trips.groupBy(F.col("pickup_date").alias("event_date"), F.col("pickup_hour").alias("hour_of_day"), "borough_key")
    return hourly.agg(F.count("*").alias("trip_count"), rounded_sum("total_amount", "revenue_usd"))


def air_hourly_by_borough():
    air = with_borough_key(silver("silver_air_quality"))
    hourly = air.groupBy(F.col("measure_date").alias("event_date"), F.col("measure_hour").alias("hour_of_day"), "borough_key")
    pivoted = hourly.pivot("parameter", AIR_PARAMETERS).agg(F.round(F.avg("value"), 3))
    return pivoted.select(*HOURLY_KEYS, *[F.col(parameter).alias(f"{parameter}_avg") for parameter in AIR_PARAMETERS])


def build_fact_mobility_air_hourly():
    hourly = taxi_hourly_by_borough().join(air_hourly_by_borough(), HOURLY_KEYS, "full")
    with_time_of_day = hourly.withColumn("time_of_day", time_of_day("hour_of_day"))
    return with_date_key(with_time_of_day, "event_date").drop("event_date")


# %%
write_table(build_fact_taxi_daily(), GOLD_LAKEHOUSE, "fact_taxi_daily")
write_table(build_fact_air_quality_daily(), GOLD_LAKEHOUSE, "fact_air_quality_daily")
write_table(build_fact_mobility_air_hourly(), GOLD_LAKEHOUSE, "fact_mobility_air_hourly")
