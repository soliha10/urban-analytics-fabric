# %%
%run nb_common

# %%
import matplotlib.pyplot as plt


def gold(table):
    return read_table(GOLD_LAKEHOUSE, table)


def with_calendar(fact):
    return fact.join(gold("dim_date"), "date_key")


def plot_lines(frame, x, columns, title):
    axis = frame.plot(x=x, y=columns, figsize=(14, 4), title=title)
    axis.grid(alpha=0.3)
    plt.show()


def plot_bars(frame, x, y, title):
    axis = frame.plot.barh(x=x, y=y, figsize=(10, 5), title=title, legend=False)
    axis.invert_yaxis()
    plt.show()


# %%
def daily_mobility():
    daily = with_calendar(gold("fact_taxi_daily")).groupBy("calendar_date").agg(
        F.sum("trip_count").alias("trips"),
        (F.sum("fare_usd") / F.sum("trip_count")).alias("avg_fare_usd"),
    )
    return daily.orderBy("calendar_date").toPandas()


def busiest_pickup_zones(limit=10):
    zones = gold("fact_taxi_daily").join(gold("dim_zone"), "zone_key").groupBy("zone_name")
    return zones.agg(F.sum("trip_count").alias("trips")).orderBy(F.desc("trips")).limit(limit).toPandas()


# %%
mobility = daily_mobility()
plot_lines(mobility, "calendar_date", ["trips"], "Mobility: trips per day")
plot_lines(mobility, "calendar_date", ["avg_fare_usd"], "Mobility: average fare (USD)")
plot_bars(busiest_pickup_zones(), "zone_name", "trips", "Mobility: busiest pickup zones")


# %%
def daily_pollution_by_borough(parameter):
    air = with_calendar(gold("fact_air_quality_daily")).join(gold("dim_borough"), "borough_key")
    daily = air.filter(F.col("parameter") == parameter).groupBy("calendar_date").pivot("borough").agg(F.avg("avg_value"))
    return daily.orderBy("calendar_date").toPandas()


# %%
for parameter in ["pm25", "no2"]:
    pollution = daily_pollution_by_borough(parameter)
    plot_lines(pollution, "calendar_date", list(pollution.columns[1:]), f"Air quality: daily {parameter} by borough")


# %%
def daily_city_mobility_air():
    trips = gold("fact_taxi_daily").groupBy("date_key").agg(F.sum("trip_count").alias("trips"))
    air = gold("fact_air_quality_daily").groupBy("date_key").pivot("parameter", AIR_PARAMETERS).agg(F.avg("avg_value"))
    return with_calendar(trips.join(air, "date_key")).orderBy("calendar_date").toPandas()


def plot_overlay(frame, pollutant):
    trips_axis = frame.plot(x="calendar_date", y="trips", figsize=(14, 4), color="tab:blue", legend=False)
    frame.plot(x="calendar_date", y=pollutant, ax=trips_axis, secondary_y=True, color="tab:red", legend=False)
    trips_axis.set_title(f"Taxi trips (blue) vs {pollutant} (red)")
    plt.show()


def plot_scatter(frame, pollutant):
    frame.plot.scatter(x="trips", y=pollutant, alpha=0.4, figsize=(6, 5), title=f"Trips vs {pollutant}")
    plt.show()


# %%
mobility_air = daily_city_mobility_air()
display(mobility_air[["trips", *AIR_PARAMETERS]].corr().round(3))
for pollutant in ["pm25", "no2"]:
    plot_overlay(mobility_air, pollutant)
    plot_scatter(mobility_air, pollutant)


# %%
def hourly_borough_correlation():
    hourly = gold("fact_mobility_air_hourly").join(gold("dim_borough"), "borough_key")
    segments = hourly.groupBy("borough", "time_of_day").agg(
        F.round(F.corr("trip_count", "pm25_avg"), 3).alias("corr_pm25"),
        F.round(F.corr("trip_count", "no2_avg"), 3).alias("corr_no2"),
        F.count("*").alias("sample_size"),
    )
    return segments.orderBy(F.desc(F.abs(F.col("corr_no2")))).toPandas()


# %%
display(hourly_borough_correlation())


# %%
def monthly_revenue():
    monthly = with_calendar(gold("fact_taxi_daily")).groupBy("year_number", "month_number").agg(
        (F.sum("revenue_usd") / F.sum("trip_count")).alias("revenue_per_trip_usd"),
        (F.sum("revenue_eur") / F.sum("trip_count")).alias("revenue_per_trip_eur"),
    )
    month_label = F.format_string("%d-%02d", "year_number", "month_number")
    return monthly.withColumn("month", month_label).orderBy("month").toPandas()


def gdp_context(country_code="USA"):
    gdp = gold("dim_gdp").filter(F.col("country_code") == country_code)
    return gdp.select("year_number", (F.col("gdp_usd") / 1e12).alias("gdp_trillion_usd")).orderBy("year_number").toPandas()


# %%
plot_lines(monthly_revenue(), "month", ["revenue_per_trip_usd", "revenue_per_trip_eur"], "Economy: revenue per trip USD vs EUR")
plot_lines(gdp_context(), "year_number", ["gdp_trillion_usd"], "Economy: USA GDP (trillion USD)")
