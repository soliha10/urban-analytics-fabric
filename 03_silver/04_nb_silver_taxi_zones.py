# %%
%run nb_common

# %%
UNKNOWN_VALUES = ["", "N/A", "NV", "Unknown"]


def clean_text(column):
    value = F.trim(F.col(column))
    return F.when(value.isNull() | value.isin(UNKNOWN_VALUES), "Unknown").otherwise(value)


def read_bronze_taxi_zones():
    return spark.read.option("header", True).csv(bronze_file_path(TAXI_ZONES_FILE))


def standardize_taxi_zones(zones):
    return zones.select(
        F.col("LocationID").cast("int").alias("zone_id"),
        clean_text("Borough").alias("borough"),
        clean_text("Zone").alias("zone_name"),
        clean_text("service_zone").alias("service_zone"),
    )


def build_silver_taxi_zones():
    return standardize_taxi_zones(read_bronze_taxi_zones()).dropDuplicates(["zone_id"])


# %%
write_table(build_silver_taxi_zones(), SILVER_LAKEHOUSE, "silver_taxi_zones")
