let
    Response = Web.Contents("https://data-api.ecb.europa.eu", [
        RelativePath = "service/data/EXR/D.USD.EUR.SP00.A",
        Query = [format = "csvdata", startPeriod = "2015-01-01"]
    ]),

    Source = Csv.Document(Response, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Selected = Table.SelectColumns(Promoted, {"TIME_PERIOD", "OBS_VALUE", "CURRENCY", "CURRENCY_DENOM"}),
    Renamed = Table.TransformColumnNames(Selected, Text.Lower),

    Typed = Table.TransformColumnTypes(Renamed, {
        {"time_period", type date}, {"obs_value", type number},
        {"currency", type text}, {"currency_denom", type text}
    }, "en-US"),

    WithIngestedAt = Table.AddColumn(Typed, "ingested_at", each DateTime.LocalNow(), type datetime)
in
    WithIngestedAt
