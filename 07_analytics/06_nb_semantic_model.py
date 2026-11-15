# %%
%pip install -q semantic-link-labs

# %%
from sempy_labs import refresh_semantic_model
from sempy_labs.tom import connect_semantic_model

SEMANTIC_MODEL = "sm_urban_analytics"
WORKSPACE = "ws_urban_analytics"
MEASURE_TABLE = "FactTaxiDaily"

RELATIONSHIPS = [
    ("FactTaxiDaily", "date_key", "DimDate", "date_key", "Many"),
    ("FactTaxiDaily", "zone_key", "DimZone", "zone_key", "Many"),
    ("DimZone", "borough_key", "DimBorough", "borough_key", "Many"),
    ("FactAirQualityDaily", "date_key", "DimDate", "date_key", "Many"),
    ("FactAirQualityDaily", "borough_key", "DimBorough", "borough_key", "Many"),
    ("FactMobilityAirHourly", "date_key", "DimDate", "date_key", "Many"),
    ("FactMobilityAirHourly", "borough_key", "DimBorough", "borough_key", "Many"),
    ("DimFX", "date_key", "DimDate", "date_key", "Many"),
]

MEASURES = {
    "Trips": "SUM ( FactTaxiDaily[trip_count] )",
    "Revenue USD": "SUM ( FactTaxiDaily[revenue_usd] )",
    "Revenue EUR": "SUM ( FactTaxiDaily[revenue_eur] )",
    "Avg Fare USD": "DIVIDE ( SUM ( FactTaxiDaily[fare_usd] ), [Trips] )",
    "Revenue per Trip USD": "DIVIDE ( [Revenue USD], [Trips] )",
    "Revenue per Trip EUR": "DIVIDE ( [Revenue EUR], [Trips] )",
    "Avg Daily Trips": "AVERAGEX ( VALUES ( DimDate[calendar_date] ), [Trips] )",
    "Avg Trip Duration Min": "AVERAGE ( FactTaxiDaily[avg_duration_min] )",
    "Trips YoY %": """
        VAR PreviousYearTrips = CALCULATE ( [Trips], SAMEPERIODLASTYEAR ( DimDate[calendar_date] ) )
        RETURN DIVIDE ( [Trips] - PreviousYearTrips, PreviousYearTrips )""",
    "Pollutant Avg": "AVERAGE ( FactAirQualityDaily[avg_value] )",
    "Pollutant Peak": "MAX ( FactAirQualityDaily[max_value] )",
    "PM2.5 Avg": "CALCULATE ( [Pollutant Avg], FactAirQualityDaily[parameter] = \"pm25\" )",
    "NO2 Avg": "CALCULATE ( [Pollutant Avg], FactAirQualityDaily[parameter] = \"no2\" )",
    "USD per EUR": "AVERAGE ( DimFX[usd_per_eur] )",
    "Revenue EUR at Period Avg Rate": "DIVIDE ( [Revenue USD], CALCULATE ( [USD per EUR], ALLSELECTED ( DimDate ) ) )",
    "FX Impact EUR": "[Revenue EUR] - [Revenue EUR at Period Avg Rate]",
    "USA GDP USD": """
        CALCULATE (
            SUM ( DimGDP[gdp_usd] ),
            DimGDP[country_code] = "USA",
            TREATAS ( VALUES ( DimDate[year_number] ), DimGDP[year_number] )
        )""",
    "Trips vs Pollutant Correlation": """
        VAR Days =
            FILTER (
                ADDCOLUMNS ( VALUES ( DimDate[calendar_date] ), "@trips", [Trips], "@pollutant", [Pollutant Avg] ),
                NOT ISBLANK ( [@trips] ) && NOT ISBLANK ( [@pollutant] )
            )
        VAR MeanTrips = AVERAGEX ( Days, [@trips] )
        VAR MeanPollutant = AVERAGEX ( Days, [@pollutant] )
        VAR Covariance = SUMX ( Days, ( [@trips] - MeanTrips ) * ( [@pollutant] - MeanPollutant ) )
        VAR TripsSpread = SUMX ( Days, ( [@trips] - MeanTrips ) ^ 2 )
        VAR PollutantSpread = SUMX ( Days, ( [@pollutant] - MeanPollutant ) ^ 2 )
        RETURN DIVIDE ( Covariance, SQRT ( TripsSpread * PollutantSpread ) )""",
}


# %%
def existing_relationships(tom):
    return {(r.FromTable.Name, r.FromColumn.Name, r.ToTable.Name) for r in tom.model.Relationships}


def add_relationships(tom):
    existing = existing_relationships(tom)
    for from_table, from_column, to_table, to_column, from_cardinality in RELATIONSHIPS:
        if (from_table, from_column, to_table) not in existing:
            tom.add_relationship(from_table, from_column, to_table, to_column, from_cardinality, "One")


def add_measures(tom):
    existing = {m.Name for m in tom.all_measures()}
    for name, expression in MEASURES.items():
        if name not in existing:
            tom.add_measure(MEASURE_TABLE, name, expression.strip())


# %%
with connect_semantic_model(dataset=SEMANTIC_MODEL, workspace=WORKSPACE, readonly=False) as tom:
    add_relationships(tom)
    add_measures(tom)
    tom.mark_as_date_table("DimDate", "calendar_date")

refresh_semantic_model(dataset=SEMANTIC_MODEL, workspace=WORKSPACE)
print(f"{len(RELATIONSHIPS)} relationships, {len(MEASURES)} measures applied to {SEMANTIC_MODEL}")
