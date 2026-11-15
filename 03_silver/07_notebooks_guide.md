# 07. Notebooklarni yaratish (Silver va Gold uchun bir xil)

## Fayl → notebook nomi
| Fayl | Fabric notebook nomi |
|---|---|
| `03_silver/01_nb_config.py` | `nb_config` |
| `03_silver/02_nb_common.py` | `nb_common` |
| `03_silver/03_nb_silver_taxi_trips.py` | `nb_silver_taxi_trips` |
| `03_silver/04_nb_silver_taxi_zones.py` | `nb_silver_taxi_zones` |
| `03_silver/05_nb_silver_air_quality.py` | `nb_silver_air_quality` |
| `03_silver/06_nb_silver_economy.py` | `nb_silver_economy` |
| `04_gold/01_nb_gold_dimensions.py` | `nb_gold_dimensions` |
| `04_gold/02_nb_gold_facts.py` | `nb_gold_facts` |
| `07_analytics/01_nb_insights.py` | `nb_insights` |

> Nomlar aynan shunday bo'lishi shart — `%run nb_config` va `%run nb_common` shu nomlarga tayanadi.

## Ko'chirish qoidasi
- Har bir `# %%` qatori = **yangi cell**. `# %%` ning o'zini ko'chirmang.
- `%run ...` qatori **alohida cell**da yolg'iz turishi kerak (fayllarda shunday ajratilgan).
- Language: **PySpark (Python)**.

## Lakehouse ulash
Har bir notebookda chap panel → **Lakehouses → Add** → `lh_silver` ni default qilib qo'shing.
Kod barcha lakehouselarga OneLake `abfss://` yo'li orqali murojaat qiladi, shuning uchun bitta default yetarli.

## Ishga tushirish tartibi
1. `nb_silver_taxi_trips`, `nb_silver_taxi_zones`, `nb_silver_air_quality`, `nb_silver_economy` (istalgan tartibda)
2. `nb_gold_dimensions`
3. `nb_gold_facts`

`nb_config` va `nb_common` ni alohida ishga tushirish shart emas.

## Natija
- `lh_silver/Tables`: `silver_taxi_trips`, `silver_taxi_zones`, `silver_air_quality`, `silver_fx_rates`, `silver_gdp`
- `lh_gold/Tables`: `dim_date`, `dim_borough`, `dim_zone`, `dim_fx`, `dim_gdp`,
  `fact_taxi_daily`, `fact_air_quality_daily`, `fact_mobility_air_hourly`
