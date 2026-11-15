# %%
%run nb_config

# %%
from functools import reduce

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def lakehouse_root(lakehouse):
    return f"abfss://{WORKSPACE_NAME}@onelake.dfs.fabric.microsoft.com/{lakehouse}.Lakehouse"


def table_path(lakehouse, table):
    return f"{lakehouse_root(lakehouse)}/Tables/{table}"


def bronze_file_path(relative_path):
    return f"{lakehouse_root(BRONZE_LAKEHOUSE)}/Files/{relative_path}"


def read_table(lakehouse, table):
    return spark.read.format("delta").load(table_path(lakehouse, table))


def write_table(df, lakehouse, table, partition_columns=()):
    writer = df.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    writer.partitionBy(*partition_columns).save(table_path(lakehouse, table))
    print(f"{lakehouse}.{table}: {read_table(lakehouse, table).count():,} rows")


# %%
def list_files(folder, extension):
    return sorted(file.path for file in notebookutils.fs.ls(folder) if file.path.endswith(extension))


def union_all(frames):
    return reduce(DataFrame.unionByName, frames)


def literal_map(mapping):
    return F.create_map(*[F.lit(item) for pair in mapping.items() for item in pair])


def rounded_sum(column, alias):
    return F.round(F.sum(column), 2).alias(alias)


# %%
def date_spine(start, end, column="calendar_date"):
    days = F.sequence(F.to_date(F.lit(str(start))), F.to_date(F.lit(str(end))))
    return spark.range(1).select(F.explode(days).alias(column))


def with_date_key(df, date_column):
    return df.withColumn("date_key", F.date_format(date_column, "yyyyMMdd").cast("int"))


def within_analysis_window(date_column):
    return F.col(date_column).between(F.to_date(F.lit(ANALYSIS_START)), F.to_date(F.lit(ANALYSIS_END)))


def is_weekend(date_column):
    return F.dayofweek(date_column).isin(1, 7)


def time_of_day(hour_column):
    hour = F.col(hour_column)
    return (
        F.when(hour.between(6, 9), "morning_rush")
        .when(hour.between(10, 15), "midday")
        .when(hour.between(16, 19), "evening_rush")
        .otherwise("night")
    )
