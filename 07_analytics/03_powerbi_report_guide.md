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

## 4. Hisobot sahifalari (avtomatik)
`nb_report_builder` notebookini (`07_nb_report_builder.py`) ishga tushiring: u Fabric REST API orqali hisobot ta'rifini
(PBIR) oladi, `definition/pages/` ni quyidagi 4 sahifa bilan almashtiradi va `updateDefinition` bilan qayta yozadi.
Hisobot `rpt_urban_analytics` nomi bilan oldindan yaratilgan bo'lishi kerak (bo'sh hisobot ham bo'ladi).
F2 capacity bir vaqtda bitta Spark sessiyasini ko'taradi — boshqa notebook sessiyalarini avval to'xtating.

| Sahifa | Vizuallar |
|---|---|
| **Mobility** | Card: `Trips`, `Avg Daily Trips`, `Avg Fare USD`, `Revenue per Trip USD`; Line: `Trips` by `calendar_date`; Bar: `Trips` by `DimZone[borough]`; Matrix: `day_name` × `time_of_day` (Sum `trip_count`); Bar: busiest `zone_name` |
| **Air Quality** | Slicer (dropdown): `FactAirQualityDaily[parameter]`; Card: `Pollutant Avg`, `Pollutant Peak`, `NO2 Avg`; Line: `Pollutant Avg` by date, legend `borough`; Bar: `Pollutant Avg` by `borough`; Matrix: `borough` × `time_of_day` (Avg `no2_avg`) |
| **Mobility vs Air** | Slicer: `parameter`; Card: `Trips vs Pollutant Correlation`, `Trips`, `Pollutant Avg`; Combo: `Trips` (column) + `Pollutant Avg` (line) by date; Scatter: X `Trips`, Y `Pollutant Avg`, details `calendar_date`; Matrix: `time_of_day` × trips, PM2.5, NO2, O3 |
| **Economic Impact** | Card: `Revenue USD`, `Revenue EUR`, `USD per EUR`, `FX Impact EUR`; Line: `Revenue per Trip USD/EUR` by `month_number`; Line: `USD per EUR` by date; Column: `Revenue USD` by `borough`; Column: `gdp_usd` by `year_number` (filter `country_code = USA`) |

## 5. Publish to web (ochiq havola)
Publish to web Direct Lake modeliga ulangan hisobotni qabul qilmaydi ("report is not eligible"). Yechim:
1. Admin portal → Tenant settings → **Publish to web** → Enabled + **Allow users to create new embed codes** → Apply.
2. `nb_public_model` (`08_nb_public_model.py`) → **Run all**: Direct Lake modelning BIM'ini olib, partitionlarni Import (M)
   ga o'giradi va `sm_urban_analytics_import` ni yaratadi. Birinchi refresh "default data connection" xatosi bilan tushadi.
3. `sm_urban_analytics_import` → Settings → **Gateway and cloud connections** → Maps to: **Create a connection**
   → OAuth 2.0 → Edit credentials → Create → `conn_wh_urban_analytics` ni tanlab **Apply**.
4. `nb_public_model` ni qayta ishga tushiring: refresh o'tadi va `rpt_urban_analytics_public` (klon) yaratiladi.
5. `rpt_urban_analytics_public` → File → Embed report → **Publish to web (public)** → Publish.

Havola: https://app.fabric.microsoft.com/view?r=eyJrIjoiMWI0MzI3NjQtYjkwOC00NWIxLWEzNDAtYWFiZWY0ZjVlODljIiwidCI6ImNkNjgxMGVmLWFiYzYtNGZjMS1hYjA1LWNmYzhhMTliNzJjNSIsImMiOjEwfQ%3D%3D
Import model ma'lumotni nusxalaydi — `pl_master` dan keyin `sm_urban_analytics_import` ni ham refresh qiling.

## 6. Saqlash
Hisobotni `rpt_urban_analytics` nomi bilan workspace'ga saqlang. Direct Lake rejimida
`pl_master` warehouse'ni yangilagach hisobot avtomatik yangi ma'lumotni ko'rsatadi.
