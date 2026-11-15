# 03. Power BI semantic model va hisobot

## 1. Semantic model
1. `wh_urban_analytics` → **New semantic model** → nomi `sm_urban_analytics`.
2. Jadvallar: `DimDate`, `DimBorough`, `DimZone`, `DimFX`, `DimGDP`, `FactTaxiDaily`,
   `FactAirQualityDaily`, `FactMobilityAirHourly`, `SecurityUserBorough`.
3. Storage mode: **Direct Lake** (default).
4. `DimDate` → **Mark as date table** → `calendar_date`.

## 2. Relationships (hammasi Many → One, single direction)
| From (many) | To (one) |
|---|---|
| `FactTaxiDaily[date_key]` | `DimDate[date_key]` |
| `FactTaxiDaily[zone_key]` | `DimZone[zone_key]` |
| `DimZone[borough_key]` | `DimBorough[borough_key]` |
| `FactAirQualityDaily[date_key]` | `DimDate[date_key]` |
| `FactAirQualityDaily[borough_key]` | `DimBorough[borough_key]` |
| `FactMobilityAirHourly[date_key]` | `DimDate[date_key]` |
| `FactMobilityAirHourly[borough_key]` | `DimBorough[borough_key]` |
| `DimFX[date_key]` | `DimDate[date_key]` |

`DimGDP` — bog'lanishsiz, `[USA GDP USD]` measure `TREATAS` orqali yil bo'yicha filtrlaydi.
`SecurityUserBorough` — bog'lanishsiz, faqat RLS uchun (yashiring).

## 3. Relationships + measures (avtomatik)
`nb_semantic_model` notebookini (`06_nb_semantic_model.py`) ishga tushiring: u 8 ta relationship, 18 ta measure qo'shadi,
`DimDate` ni date table qiladi va modelni refresh qiladi. Qo'lda qilish kerak bo'lsa — `02_powerbi_measures.dax`
dagi har bir measure'ni `FactTaxiDaily` jadvalida **New measure** orqali qo'shing.

## 4. Hisobot sahifalari
| Sahifa | Vizuallar |
|---|---|
| **Mobility** | Card: `Trips`, `Avg Daily Trips`, `Avg Fare USD`; Line: `Trips` by `calendar_date`; Bar: `Trips` by `DimZone[zone_name]` (Top N 10); Matrix: `day_name` × `FactMobilityAirHourly[hour_of_day]` |
| **Air Quality** | Slicer: `FactAirQualityDaily[parameter]`; Line: `Pollutant Avg` by date, legend `borough`; Map/Bar: `Pollutant Avg` by `borough`; Card: `Pollutant Peak` |
| **Mobility vs Air** | Slicer: `parameter`; Line + clustered column: `Trips` (column) va `Pollutant Avg` (line) by date; Scatter: X `Trips`, Y `Pollutant Avg`, details `calendar_date`; Card: `Trips vs Pollutant Correlation` |
| **Economic Impact** | Line: `Revenue per Trip USD` va `Revenue per Trip EUR` by month; Line: `USD per EUR`; Card: `FX Impact EUR`; Column: `USA GDP USD` by `year_number`; Card: `Trips YoY %` |

## 5. Publish
Hisobotni `rpt_urban_analytics` nomi bilan workspace'ga saqlang. Direct Lake rejimida
`pl_master` warehouse'ni yangilagach hisobot avtomatik yangi ma'lumotni ko'rsatadi.
