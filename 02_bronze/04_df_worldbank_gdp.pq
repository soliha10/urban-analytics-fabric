let
    Countries = "USA;CHN;DEU;GBR;JPN;FRA;IND;EUU;WLD",
    Indicator = "NY.GDP.MKTP.CD",
    YearRange = "2000:2025",

    Response = Json.Document(Web.Contents("https://api.worldbank.org", [
        RelativePath = "v2/country/" & Countries & "/indicator/" & Indicator,
        Query = [format = "json", per_page = "20000", date = YearRange]
    ])),

    ToGdpRow = (observation as record) as record => [
        country_code = observation[countryiso3code],
        country_name = observation[country][value],
        indicator_code = observation[indicator][id],
        year = observation[date],
        gdp_usd = observation[value]
    ],

    AsTable = Table.FromRecords(List.Transform(Response{1}, ToGdpRow)),

    Typed = Table.TransformColumnTypes(AsTable, {
        {"country_code", type text}, {"country_name", type text},
        {"indicator_code", type text}, {"year", Int64.Type}, {"gdp_usd", type number}
    }),

    WithIngestedAt = Table.AddColumn(Typed, "ingested_at", each DateTime.LocalNow(), type datetime)
in
    WithIngestedAt
