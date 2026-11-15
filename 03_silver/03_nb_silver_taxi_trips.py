# %%
%run nb_common

# %%
TAXI_COLUMNS = {
    "VendorID": ("vendor_id", "int"),
    "tpep_pickup_datetime": ("pickup_ts", "timestamp"),
    "tpep_dropoff_datetime": ("dropoff_ts", "timestamp"),
    "passenger_count": ("passenger_count", "int"),
    "trip_distance": ("trip_distance", "double"),
    "PULocationID": ("pickup_zone_id", "int"),
    "DOLocationID": ("dropoff_zone_id", "int"),
    "payment_type": ("payment_type", "int"),
    "fare_amount": ("fare_amount", "double"),
    "tip_amount": ("tip_amount", "double"),
    "total_amount": ("total_amount", "double"),
}

TRIP_IDENTITY = ["vendor_id", "pickup_ts", "dropoff_ts", "pickup_zone_id", "dropoff_zone_id", "total_amount"]


# %%
def read_taxi_file(path):
    raw = spark.read.parquet(path)
    return raw.select([F.col(source).cast(dtype).alias(target) for source, (target, dtype) in TAXI_COLUMNS.items()])


def read_bronze_taxi_trips():
    paths = list_files(bronze_file_path(TAXI_TRIPS_FOLDER), ".parquet")
    return union_all([read_taxi_file(path) for path in paths])


def add_trip_metrics(trips):
    duration_seconds = F.unix_timestamp("dropoff_ts") - F.unix_timestamp("pickup_ts")
    return (
        trips.withColumn("pickup_date", F.to_date("pickup_ts"))
        .withColumn("pickup_hour", F.hour("pickup_ts"))
        .withColumn("duration_min", F.round(duration_seconds / 60, 2))
    )


def is_valid_trip():
    return (
        within_analysis_window("pickup_date")
        & F.col("duration_min").between(1, 240)
        & F.col("trip_distance").between(0.1, 200)
        & (F.col("fare_amount") >= 0)
        & (F.col("total_amount") > 0)
    )


def add_calendar_attributes(trips):
    return (
        trips.withColumn("pickup_year", F.year("pickup_date"))
        .withColumn("pickup_month", F.month("pickup_date"))
        .withColumn("is_weekend", is_weekend("pickup_date"))
        .withColumn("time_of_day", time_of_day("pickup_hour"))
    )


def build_silver_taxi_trips():
    valid_trips = add_trip_metrics(read_bronze_taxi_trips()).filter(is_valid_trip())
    return add_calendar_attributes(valid_trips.dropDuplicates(TRIP_IDENTITY))


# %%
write_table(build_silver_taxi_trips(), SILVER_LAKEHOUSE, "silver_taxi_trips", ["pickup_year", "pickup_month"])
