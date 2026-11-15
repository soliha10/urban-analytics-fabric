# %%
%run nb_common

# %%
def build_dim_date():
    dates = with_date_key(date_spine(ANALYSIS_START, ANALYSIS_END), "calendar_date")
    return dates.select(
        "date_key",
        "calendar_date",
        F.year("calendar_date").alias("year_number"),
        F.quarter("calendar_date").alias("quarter_number"),
        F.month("calendar_date").alias("month_number"),
        F.date_format("calendar_date", "MMMM").alias("month_name"),
        F.dayofmonth("calendar_date").alias("day_of_month"),
        F.dayofweek("calendar_date").alias("day_of_week"),
        F.date_format("calendar_date", "EEEE").alias("day_name"),
        is_weekend("calendar_date").alias("is_weekend"),
    )


# %%
def build_dim_borough():
    boroughs = read_table(SILVER_LAKEHOUSE, "silver_taxi_zones").select("borough").distinct()
    return boroughs.select(F.row_number().over(Window.orderBy("borough")).alias("borough_key"), "borough")


def build_dim_zone():
    zones = read_table(SILVER_LAKEHOUSE, "silver_taxi_zones")
    with_borough = zones.join(read_table(GOLD_LAKEHOUSE, "dim_borough"), "borough")
    return with_borough.select(F.col("zone_id").alias("zone_key"), "zone_name", "service_zone", "borough_key", "borough")


# %%
def forward_fill(df, order_column, columns):
    history = Window.orderBy(order_column).rowsBetween(Window.unboundedPreceding, 0)
    return df.select(order_column, *[F.last(column, ignorenulls=True).over(history).alias(column) for column in columns])


def build_dim_fx():
    rates = read_table(SILVER_LAKEHOUSE, "silver_fx_rates").withColumnRenamed("rate_date", "calendar_date")
    first_rate_date = rates.agg(F.min("calendar_date")).first()[0]
    every_day = date_spine(first_rate_date, ANALYSIS_END).join(rates, "calendar_date", "left")
    filled = forward_fill(every_day, "calendar_date", ["usd_per_eur", "eur_per_usd"])
    return with_date_key(filled.filter(within_analysis_window("calendar_date")), "calendar_date").drop("calendar_date")


def build_dim_gdp():
    gdp = read_table(SILVER_LAKEHOUSE, "silver_gdp")
    previous_year_gdp = F.lag("gdp_usd").over(Window.partitionBy("country_code").orderBy("year_number"))
    return gdp.withColumn("gdp_growth_pct", F.round((F.col("gdp_usd") / previous_year_gdp - 1) * 100, 2))


# %%
write_table(build_dim_date(), GOLD_LAKEHOUSE, "dim_date")
write_table(build_dim_borough(), GOLD_LAKEHOUSE, "dim_borough")
write_table(build_dim_zone(), GOLD_LAKEHOUSE, "dim_zone")
write_table(build_dim_fx(), GOLD_LAKEHOUSE, "dim_fx")
write_table(build_dim_gdp(), GOLD_LAKEHOUSE, "dim_gdp")
