import datetime as dt
import os
import random
import sys
import tempfile
import types
from pathlib import Path

os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

import matplotlib

matplotlib.use("Agg")

import pandas as pd
from pyspark.sql import SparkSession

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAKE_ROOT = Path(tempfile.mkdtemp(prefix="fabric_smoke_"))

SHARED_NOTEBOOKS = ["03_silver/01_nb_config.py", "03_silver/02_nb_common.py"]

PIPELINE_NOTEBOOKS = [
    "03_silver/03_nb_silver_taxi_trips.py",
    "03_silver/04_nb_silver_taxi_zones.py",
    "03_silver/05_nb_silver_air_quality.py",
    "03_silver/06_nb_silver_economy.py",
    "04_gold/01_nb_gold_dimensions.py",
    "04_gold/02_nb_gold_facts.py",
    "07_analytics/01_nb_insights.py",
]

GOLD_TABLES = [
    "dim_date", "dim_borough", "dim_zone", "dim_fx", "dim_gdp",
    "fact_taxi_daily", "fact_air_quality_daily", "fact_mobility_air_hourly",
]

ZONE_LOOKUP = {
    "LocationID": [1, 132, 161, 236, 264],
    "Borough": ["EWR", "Queens", "Manhattan", "Manhattan", "Unknown"],
    "Zone": ["Newark Airport", "JFK Airport", "Midtown Center", "Upper East Side North", "N/A"],
    "service_zone": ["EWR", "Airports", "Yellow Zone", "Yellow Zone", "N/A"],
}

AIR_STATIONS = {10: (40.75, -73.98), 20: (40.66, -73.95), 30: (41.50, -73.00)}
AIR_SENSORS = [("PM2.5", "µg/m³", 1), ("no2", "ppm", 1000), ("o3", "ppm", 1000)]
OPENAQ_COLUMNS = "location_id location_name latitude longitude sensor_id parameter units datetime_utc datetime_local value"


def create_spark():
    spark = SparkSession.builder.master("local[2]").config("spark.sql.shuffle.partitions", "2").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def local_notebookutils():
    def list_folder(folder):
        return [types.SimpleNamespace(path=str(path)) for path in Path(folder).iterdir()]

    return types.SimpleNamespace(fs=types.SimpleNamespace(ls=list_folder))


def notebook_code(relative_path):
    lines = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8").splitlines()
    return "\n".join(line for line in lines if not line.startswith("%run"))


def run_notebook(namespace, relative_path):
    print(f"==> {relative_path}")
    exec(compile(notebook_code(relative_path), relative_path, "exec"), namespace)


def use_local_lake(namespace, spark):
    def read_table(lakehouse, table):
        return spark.read.parquet(namespace["table_path"](lakehouse, table))

    def write_table(df, lakehouse, table, partition_columns=()):
        df.write.mode("overwrite").partitionBy(*partition_columns).parquet(namespace["table_path"](lakehouse, table))
        print(f"{lakehouse}.{table}: {read_table(lakehouse, table).count():,} rows")

    namespace["lakehouse_root"] = lambda lakehouse: str(LAKE_ROOT / lakehouse)
    namespace.update(read_table=read_table, write_table=write_table)


def build_namespace(spark):
    namespace = {"spark": spark, "notebookutils": local_notebookutils(), "display": print}
    for relative_path in SHARED_NOTEBOOKS:
        run_notebook(namespace, relative_path)
    use_local_lake(namespace, spark)
    return namespace


def bronze_path(relative_path):
    path = LAKE_ROOT / "lh_bronze" / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def random_trip(month):
    pickup = dt.datetime(2024, month, 1) + dt.timedelta(minutes=random.randint(0, 40000))
    return {
        "VendorID": 1,
        "tpep_pickup_datetime": pickup,
        "tpep_dropoff_datetime": pickup + dt.timedelta(minutes=random.randint(0, 60)),
        "passenger_count": random.randint(1, 4),
        "trip_distance": random.uniform(0, 10),
        "PULocationID": random.choice([132, 161, 236, 264]),
        "DOLocationID": 161,
        "payment_type": 1,
        "fare_amount": random.uniform(-5, 50),
        "tip_amount": 2.0,
        "total_amount": random.uniform(5, 60),
    }


def write_taxi_month(month, passenger_type):
    trips = pd.DataFrame([random_trip(month) for _ in range(400)])
    trips = pd.concat([trips, trips.head(1)]).astype({"passenger_count": passenger_type})
    trips.to_parquet(bronze_path(f"Files/taxi/yellow/yellow_tripdata_2024-{month:02d}.parquet"))


def write_zone_lookup():
    pd.DataFrame(ZONE_LOOKUP).to_csv(bronze_path("Files/taxi/reference/taxi_zone_lookup.csv"), index=False)


def air_reading(location_id, coordinates, sensor, hour):
    parameter, units, scale = sensor
    measured = dt.datetime(2024, 1, 1) + dt.timedelta(hours=hour)
    return (
        location_id, f"Station {location_id}", *coordinates, location_id * 10 + len(parameter), parameter, units,
        measured.strftime("%Y-%m-%dT%H:%M:%SZ"), measured.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
        random.uniform(-1, 30) / scale,
    )


def write_openaq(spark):
    readings = [
        air_reading(location_id, coordinates, sensor, hour)
        for location_id, coordinates in AIR_STATIONS.items()
        for sensor in AIR_SENSORS
        for hour in range(24 * 40)
    ]
    spark.createDataFrame(readings, OPENAQ_COLUMNS.split()).write.parquet(bronze_path("Tables/bronze_openaq_hourly"))


def write_ecb_fx(spark):
    days = [dt.date(2023, 12, 1) + dt.timedelta(days=offset) for offset in range(120)]
    rates = [(str(day), 1.05 + index / 1000, "USD", "EUR") for index, day in enumerate(days) if day.weekday() < 5]
    schema = "time_period string, obs_value double, currency string, currency_denom string"
    spark.createDataFrame(rates, schema).write.parquet(bronze_path("Tables/bronze_ecb_fx"))


def write_worldbank_gdp(spark):
    rows = [("USA", "United States", "NY.GDP.MKTP.CD", year, 2.0e13 + year * 1e11) for year in range(2020, 2025)]
    rows.append(("WLD", "World", "NY.GDP.MKTP.CD", 2023, None))
    schema = "country_code string, country_name string, indicator_code string, year long, gdp_usd double"
    spark.createDataFrame(rows, schema).write.parquet(bronze_path("Tables/bronze_worldbank_gdp"))


def write_bronze_sample(spark):
    random.seed(1)
    write_taxi_month(1, "int64")
    write_taxi_month(2, "float64")
    write_zone_lookup()
    write_openaq(spark)
    write_ecb_fx(spark)
    write_worldbank_gdp(spark)


def check(condition, message):
    print(f"{'PASS' if condition else 'FAIL'}: {message}")
    return condition


def run_checks(read_table):
    air = read_table("lh_silver", "silver_air_quality")
    units = {row.parameter: row.units for row in air.select("parameter", "units").distinct().collect()}
    trips = read_table("lh_silver", "silver_taxi_trips")
    return [
        *[check(read_table("lh_gold", table).count() > 0, f"lh_gold.{table} has rows") for table in GOLD_TABLES],
        check(units == {"pm25": "µg/m³", "no2": "ppb", "o3": "ppb"}, f"air units standardized {units}"),
        check(air.filter("location_id = 30").count() == 0, "station outside NYC removed"),
        check(trips.filter("fare_amount < 0 or duration_min < 1").count() == 0, "invalid trips removed"),
        check(read_table("lh_gold", "dim_fx").filter("usd_per_eur is null").count() == 0, "FX forward-filled every day"),
    ]


def main():
    spark = create_spark()
    namespace = build_namespace(spark)
    write_bronze_sample(spark)
    for relative_path in PIPELINE_NOTEBOOKS:
        run_notebook(namespace, relative_path)
    results = run_checks(namespace["read_table"])
    print(f"\n{sum(results)}/{len(results)} checks passed. Local lake: {LAKE_ROOT}")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
