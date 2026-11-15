# %%
WORKSPACE_NAME = "ws_urban_analytics"

BRONZE_LAKEHOUSE = "lh_bronze"
SILVER_LAKEHOUSE = "lh_silver"
GOLD_LAKEHOUSE = "lh_gold"

TAXI_TRIPS_FOLDER = "taxi/yellow"
TAXI_ZONES_FILE = "taxi/reference/taxi_zone_lookup.csv"

ANALYSIS_START = "2024-01-01"
ANALYSIS_END = "2024-03-31"

AIR_PARAMETERS = ["pm25", "no2", "o3"]

STANDARD_UNITS = {"pm25": "µg/m³", "no2": "ppb", "o3": "ppb"}

UNIT_CONVERSIONS = [
    ("no2", "ppm", 1000.0),
    ("o3", "ppm", 1000.0),
    ("no2", "µg/m³", 1 / 1.88),
    ("o3", "µg/m³", 1 / 1.96),
]

NYC_BOUNDS = {"min_lat": 40.49, "max_lat": 40.92, "min_lon": -74.26, "max_lon": -73.70}

BOROUGH_CENTROIDS = {
    "Manhattan": (40.7831, -73.9712),
    "Brooklyn": (40.6782, -73.9442),
    "Queens": (40.7282, -73.7949),
    "Bronx": (40.8448, -73.8648),
    "Staten Island": (40.5795, -74.1502),
}
