# %%
%run nb_common

# %%
def normalized_parameter(column):
    return F.lower(F.regexp_replace(F.col(column), "[^A-Za-z0-9]", ""))


def local_timestamp(column):
    return F.to_timestamp(F.substring(F.col(column), 1, 19))


def standardize_measurements(measurements):
    return measurements.select(
        F.col("sensor_id").cast("long"),
        F.col("location_id").cast("long"),
        F.trim("location_name").alias("location_name"),
        F.col("latitude").cast("double"),
        F.col("longitude").cast("double"),
        normalized_parameter("parameter").alias("parameter"),
        F.trim("units").alias("units"),
        local_timestamp("datetime_local").alias("measured_at"),
        F.col("value").cast("double"),
    )


# %%
def is_inside_nyc():
    return F.col("latitude").between(NYC_BOUNDS["min_lat"], NYC_BOUNDS["max_lat"]) & F.col("longitude").between(
        NYC_BOUNDS["min_lon"], NYC_BOUNDS["max_lon"]
    )


def is_valid_measurement():
    return (
        F.col("parameter").isin(AIR_PARAMETERS)
        & F.col("measured_at").isNotNull()
        & (F.col("value") >= 0)
        & is_inside_nyc()
    )


def add_time_attributes(measurements):
    return measurements.withColumn("measure_date", F.to_date("measured_at")).withColumn(
        "measure_hour", F.hour("measured_at")
    )


# %%
def unit_conversion_factors():
    return spark.createDataFrame(UNIT_CONVERSIONS, ["parameter", "units", "factor"])


def to_standard_units(measurements):
    converted = measurements.join(F.broadcast(unit_conversion_factors()), ["parameter", "units"], "left")
    return (
        converted.withColumn("value", F.round(F.col("value") * F.coalesce("factor", F.lit(1.0)), 3))
        .withColumn("units", literal_map(STANDARD_UNITS)[F.col("parameter")])
        .drop("factor")
    )


# %%
def borough_centroids():
    rows = [(borough, lat, lon) for borough, (lat, lon) in BOROUGH_CENTROIDS.items()]
    return spark.createDataFrame(rows, ["borough", "borough_lat", "borough_lon"])


def squared_distance_to_borough():
    return (F.col("latitude") - F.col("borough_lat")) ** 2 + (F.col("longitude") - F.col("borough_lon")) ** 2


def nearest_borough(locations):
    ranked = locations.crossJoin(borough_centroids()).withColumn("distance", squared_distance_to_borough())
    closest_first = Window.partitionBy("location_id").orderBy("distance")
    return ranked.withColumn("rank", F.row_number().over(closest_first)).filter("rank = 1").select("location_id", "borough")


# %%
def build_silver_air_quality():
    raw = standardize_measurements(read_table(BRONZE_LAKEHOUSE, "bronze_openaq_hourly"))
    measurements = add_time_attributes(raw.filter(is_valid_measurement()).dropDuplicates(["sensor_id", "measured_at"]))
    in_window = to_standard_units(measurements.filter(within_analysis_window("measure_date")))
    locations = in_window.select("location_id", "latitude", "longitude").distinct()
    return in_window.join(nearest_borough(locations), "location_id")


# %%
write_table(build_silver_air_quality(), SILVER_LAKEHOUSE, "silver_air_quality", ["parameter"])
