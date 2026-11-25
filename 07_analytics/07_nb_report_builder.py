# %%
import base64
import json
import time

import sempy.fabric as fabric

REPORT_NAME = "rpt_urban_analytics"
MEASURE_TABLE = "FactTaxiDaily"
SCHEMA_ROOT = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
PAGE_SIZE = {"width": 1280, "height": 720}
SUM, AVERAGE = 0, 1
AGGREGATION_NAMES = {SUM: "Sum", AVERAGE: "Avg"}

client = fabric.FabricRestClient()
workspace_id = fabric.get_workspace_id()


# %%
def source(table, name):
    return {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}


def projection(field, query_ref):
    return {"field": field, "queryRef": query_ref}


def measure(name):
    return projection({"Measure": source(MEASURE_TABLE, name)}, f"{MEASURE_TABLE}.{name}")


def column(table, name):
    return projection({"Column": source(table, name)}, f"{table}.{name}")


def total(table, name, function=SUM):
    field = {"Aggregation": {"Expression": {"Column": source(table, name)}, "Function": function}}
    return projection(field, f"{AGGREGATION_NAMES[function]}({table}.{name})")


def literal(value):
    text = f"'{value}'" if isinstance(value, str) else str(value).lower()
    return {"expr": {"Literal": {"Value": text}}}


# %%
def visual(name, visual_type, box, title, **roles):
    return {
        "$schema": f"{SCHEMA_ROOT}/visualContainer/1.0.0/schema.json",
        "name": name,
        "position": {"x": box[0], "y": box[1], "z": 0, "width": box[2], "height": box[3]},
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": {role: {"projections": items} for role, items in roles.items()}},
            "visualContainerObjects": {"title": [{"properties": {"show": literal(True), "text": literal(title)}}]},
        },
    }


def with_objects(container, **objects):
    settings = {name: [{"properties": {key: literal(value) for key, value in values.items()}}] for name, values in objects.items()}
    return {**container, "visual": {**container["visual"], "objects": settings}}


def sorted_descending(container, projection_item):
    sort = {"sort": [{"field": projection_item["field"], "direction": "Descending"}], "isDefaultSort": False}
    return {**container, "visual": {**container["visual"], "query": {**container["visual"]["query"], "sortDefinition": sort}}}


def ranked_bar(name, box, title, category, value):
    bar = visual(name, "clusteredBarChart", box, title, Category=[category], Y=[value])
    return sorted_descending(bar, value)


def card(name, slot, measure_name):
    tile = visual(name, "card", (20 + slot * 315, 20, 300, 110), measure_name, Values=[measure(measure_name)])
    return with_objects(tile, categoryLabels={"show": False})


def card_row(prefix, measure_names, first_slot=0):
    return [card(f"{prefix}_card_{slot}", slot, name) for slot, name in enumerate(measure_names, first_slot)]


def parameter_slicer(name):
    slicer = visual(name, "slicer", (20, 20, 300, 110), "Pollutant", Values=[column("FactAirQualityDaily", "parameter")])
    return with_objects(slicer, data={"mode": "Dropdown"})


def country_filter(table, column_name, value):
    condition = {"In": {
        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": column_name}}],
        "Values": [[{"Literal": {"Value": f"'{value}'"}}]],
    }}
    query = {"Version": 2, "From": [{"Name": "t", "Entity": table, "Type": 0}], "Where": [{"Condition": condition}]}
    return {"name": f"filter_{column_name}", "field": column(table, column_name)["field"], "type": "Categorical", "filter": query}


def with_filter(container, report_filter):
    return {**container, "filterConfig": {"filters": [report_filter]}}


# %%
def mobility_page():
    return card_row("mobility", ["Trips", "Avg Daily Trips", "Avg Fare USD", "Revenue per Trip USD"]) + [
        visual("mobility_trend", "lineChart", (20, 150, 760, 270), "Daily Trips",
               Category=[column("DimDate", "calendar_date")], Y=[measure("Trips")]),
        ranked_bar("mobility_borough", (800, 150, 460, 270), "Trips by Borough", column("DimZone", "borough"), measure("Trips")),
        visual("mobility_rhythm", "pivotTable", (20, 440, 620, 260), "Trips by Day and Time of Day",
               Rows=[column("DimDate", "day_name")], Columns=[column("FactMobilityAirHourly", "time_of_day")],
               Values=[total("FactMobilityAirHourly", "trip_count")]),
        ranked_bar("mobility_zones", (660, 440, 600, 260), "Busiest Pickup Zones", column("DimZone", "zone_name"), measure("Trips")),
    ]


def air_quality_page():
    return [parameter_slicer("air_slicer")] + card_row("air", ["Pollutant Avg", "Pollutant Peak", "NO2 Avg"], 1) + [
        visual("air_trend", "lineChart", (20, 150, 760, 270), "Daily Pollutant Average by Borough",
               Category=[column("DimDate", "calendar_date")], Series=[column("DimBorough", "borough")],
               Y=[measure("Pollutant Avg")]),
        ranked_bar("air_borough", (800, 150, 460, 270), "Pollutant Average by Borough",
                   column("DimBorough", "borough"), measure("Pollutant Avg")),
        visual("air_rhythm", "pivotTable", (20, 440, 1240, 260), "Hourly NO2 (ppb) by Borough and Time of Day",
               Rows=[column("DimBorough", "borough")], Columns=[column("FactMobilityAirHourly", "time_of_day")],
               Values=[total("FactMobilityAirHourly", "no2_avg", AVERAGE)]),
    ]


def mobility_vs_air_page():
    return [parameter_slicer("link_slicer")] + card_row("link", ["Trips vs Pollutant Correlation", "Trips", "Pollutant Avg"], 1) + [
        visual("link_combo", "lineClusteredColumnComboChart", (20, 150, 1240, 270), "Daily Trips vs Pollutant Average",
               Category=[column("DimDate", "calendar_date")], Y=[measure("Trips")], Y2=[measure("Pollutant Avg")]),
        visual("link_scatter", "scatterChart", (20, 440, 620, 260), "Trips vs Pollutant (one point per day)",
               Category=[column("DimDate", "calendar_date")], X=[measure("Trips")], Y=[measure("Pollutant Avg")]),
        visual("link_hourly", "pivotTable", (660, 440, 600, 260), "Hourly Trips and Pollutants by Time of Day",
               Rows=[column("FactMobilityAirHourly", "time_of_day")],
               Values=[total("FactMobilityAirHourly", "trip_count"), total("FactMobilityAirHourly", "pm25_avg", AVERAGE),
                       total("FactMobilityAirHourly", "no2_avg", AVERAGE), total("FactMobilityAirHourly", "o3_avg", AVERAGE)]),
    ]


def economic_page():
    gdp_chart = visual("economy_gdp", "clusteredColumnChart", (660, 440, 600, 260), "USA GDP (USD) by Year",
                       Category=[column("DimGDP", "year_number")], Y=[total("DimGDP", "gdp_usd")])
    return card_row("economy", ["Revenue USD", "Revenue EUR", "USD per EUR", "FX Impact EUR"]) + [
        visual("economy_revenue", "lineChart", (20, 150, 760, 270), "Revenue per Trip by Month (USD vs EUR)",
               Category=[column("DimDate", "month_number")],
               Y=[measure("Revenue per Trip USD"), measure("Revenue per Trip EUR")]),
        visual("economy_fx", "lineChart", (800, 150, 460, 270), "USD per EUR (ECB)",
               Category=[column("DimDate", "calendar_date")], Y=[measure("USD per EUR")]),
        visual("economy_trips", "clusteredColumnChart", (20, 440, 620, 260), "Revenue USD by Borough",
               Category=[column("DimZone", "borough")], Y=[measure("Revenue USD")]),
        with_filter(gdp_chart, country_filter("DimGDP", "country_code", "USA")),
    ]


PAGES = [
    ("mobility", "Mobility", mobility_page()),
    ("air_quality", "Air Quality", air_quality_page()),
    ("mobility_vs_air", "Mobility vs Air", mobility_vs_air_page()),
    ("economic_impact", "Economic Impact", economic_page()),
]


# %%
def part(path, content):
    payload = base64.b64encode(json.dumps(content).encode("utf-8")).decode("ascii")
    return {"path": path, "payload": payload, "payloadType": "InlineBase64"}


def page_parts(name, display_name, visuals):
    folder = f"definition/pages/{name}"
    header = {"$schema": f"{SCHEMA_ROOT}/page/1.0.0/schema.json", "name": name,
              "displayName": display_name, "displayOption": "FitToPage", **PAGE_SIZE}
    return [part(f"{folder}/page.json", header)] + [part(f"{folder}/visuals/{v['name']}/visual.json", v) for v in visuals]


def pages_metadata_part():
    order = [name for name, _, _ in PAGES]
    metadata = {"$schema": f"{SCHEMA_ROOT}/pagesMetadata/1.0.0/schema.json", "pageOrder": order, "activePageName": order[0]}
    return part("definition/pages/pages.json", metadata)


def report_parts(current_parts):
    kept = [p for p in current_parts if not p["path"].startswith("definition/pages/")]
    return kept + [pages_metadata_part()] + [p for page in PAGES for p in page_parts(*page)]


# %%
def await_operation(response):
    operation_id = response.headers["x-ms-operation-id"]
    while (state := client.get(f"v1/operations/{operation_id}").json())["status"] in ("NotStarted", "Running"):
        time.sleep(3)
    if state["status"] != "Succeeded":
        raise RuntimeError(state)
    return operation_id


def report_api(report_id, action, body=None):
    return client.post(f"v1/workspaces/{workspace_id}/reports/{report_id}/{action}", json=body)


def get_report_parts(report_id):
    response = report_api(report_id, "getDefinition?format=PBIR")
    if response.status_code == 202:
        response = client.get(f"v1/operations/{await_operation(response)}/result")
    return response.json()["definition"]["parts"]


def update_report_parts(report_id, parts):
    response = report_api(report_id, "updateDefinition", {"definition": {"parts": parts}})
    if response.status_code == 202:
        await_operation(response)


def find_report_id():
    reports = client.get(f"v1/workspaces/{workspace_id}/reports").json()["value"]
    return next(report["id"] for report in reports if report["displayName"] == REPORT_NAME)


# %%
report_id = find_report_id()
update_report_parts(report_id, report_parts(get_report_parts(report_id)))
print(f"{REPORT_NAME}: {len(PAGES)} pages, {sum(len(visuals) for _, _, visuals in PAGES)} visuals published")
