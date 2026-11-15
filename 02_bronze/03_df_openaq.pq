let
    BaseUrl = "https://api.openaq.org",
    PageSize = 1000,
    NycCoordinates = "40.7128,-74.0060",
    RadiusMeters = "25000",
    TargetParameters = {"pm25", "no2", "o3"},
    DateFrom = #date(2024, 1, 1),
    DateTo = #date(2024, 4, 1),

    MonthStarts = List.Generate(() => DateFrom, each _ < DateTo, each Date.AddMonths(_, 1)),

    ToUtcText = (day as date) as text => Date.ToText(day, "yyyy-MM-dd") & "T00:00:00Z",

    Fetch = (path as text, query as record) as record =>
        Json.Document(Web.Contents(BaseUrl, [
            RelativePath = path,
            Query = query,
            Headers = [#"X-API-Key" = OpenAQApiKey]
        ])),

    FetchAfter = (path as text, query as record, seconds as number) as record =>
        Function.InvokeAfter(() => Fetch(path, query), #duration(0, 0, 0, seconds)),

    GetJson = (path as text, query as record) as record =>
        try FetchAfter(path, query, 1)
        otherwise try FetchAfter(path, query, 10)
        otherwise [results = {}],

    GetPage = (path as text, query as record, page as number) as list =>
        GetJson(path, query & [limit = Text.From(PageSize), page = Text.From(page)])[results],

    GetNextPage = (path as text, query as record, state as record) as list =>
        if List.Count(state[rows]) < PageSize then {} else GetPage(path, query, state[page] + 1),

    GetAllPages = (path as text, query as record) as list =>
        List.Combine(List.Generate(
            () => [page = 1, rows = GetPage(path, query, 1)],
            each not List.IsEmpty([rows]),
            each [page = [page] + 1, rows = GetNextPage(path, query, _)],
            each [rows]
        )),

    ToSensorRow = (location as record, sensor as record) as record => [
        location_id = location[id],
        location_name = location[name],
        latitude = location[coordinates][latitude],
        longitude = location[coordinates][longitude],
        sensor_id = sensor[id],
        parameter = sensor[parameter][name],
        units = sensor[parameter][units]
    ],

    ToSensorRows = (location as record) as list =>
        List.Transform(location[sensors], each ToSensorRow(location, _)),

    ToMeasurementRow = (sensor as record, measurement as record) as record => sensor & [
        datetime_utc = measurement[period][datetimeFrom][utc],
        datetime_local = measurement[period][datetimeFrom][local],
        value = measurement[value]
    ],

    GetSensorMonth = (sensor as record, monthStart as date) as list =>
        GetAllPages(
            "v3/sensors/" & Text.From(sensor[sensor_id]) & "/hours",
            [datetime_from = ToUtcText(monthStart), datetime_to = ToUtcText(Date.AddMonths(monthStart, 1))]
        ),

    GetSensorHours = (sensor as record) as list =>
        List.Transform(
            List.Combine(List.Transform(MonthStarts, each GetSensorMonth(sensor, _))),
            each ToMeasurementRow(sensor, _)
        ),

    Locations = GetAllPages("v3/locations", [coordinates = NycCoordinates, radius = RadiusMeters, monitor = "true"]),
    AllSensors = List.Combine(List.Transform(Locations, ToSensorRows)),
    TargetSensors = List.Select(AllSensors, each List.Contains(TargetParameters, [parameter])),
    Measurements = List.Combine(List.Transform(TargetSensors, GetSensorHours)),

    AsTable = Table.FromRecords(Measurements, {
        "location_id", "location_name", "latitude", "longitude",
        "sensor_id", "parameter", "units", "datetime_utc", "datetime_local", "value"
    }),

    Typed = Table.TransformColumnTypes(AsTable, {
        {"location_id", Int64.Type}, {"location_name", type text},
        {"latitude", type number}, {"longitude", type number},
        {"sensor_id", Int64.Type}, {"parameter", type text}, {"units", type text},
        {"datetime_utc", type text}, {"datetime_local", type text}, {"value", type number}
    }),

    WithIngestedAt = Table.AddColumn(Typed, "ingested_at", each DateTime.LocalNow(), type datetime)
in
    WithIngestedAt
