# %%
%run nb_common

# %%
def build_silver_fx_rates():
    fx = read_table(BRONZE_LAKEHOUSE, "bronze_ecb_fx").select(
        F.to_date("time_period").alias("rate_date"),
        F.col("obs_value").cast("double").alias("usd_per_eur"),
    )
    valid_rates = fx.filter(F.col("usd_per_eur") > 0).dropDuplicates(["rate_date"])
    return valid_rates.withColumn("eur_per_usd", F.round(1 / F.col("usd_per_eur"), 6))


def build_silver_gdp():
    gdp = read_table(BRONZE_LAKEHOUSE, "bronze_worldbank_gdp").select(
        F.upper(F.trim("country_code")).alias("country_code"),
        F.trim("country_name").alias("country_name"),
        F.col("year").cast("int").alias("year_number"),
        F.col("gdp_usd").cast("double"),
    )
    return gdp.filter(F.col("gdp_usd").isNotNull()).dropDuplicates(["country_code", "year_number"])


# %%
write_table(build_silver_fx_rates(), SILVER_LAKEHOUSE, "silver_fx_rates")
write_table(build_silver_gdp(), SILVER_LAKEHOUSE, "silver_gdp")
