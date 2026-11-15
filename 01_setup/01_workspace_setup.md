# 01. Fabric workspace sozlash

## 1. Workspace
1. https://app.fabric.microsoft.com → **Workspaces → New workspace**.
2. Nomi: `ws_urban_analytics` (bo'sh joysiz! Notebooklar OneLake yo'lini shu nomdan quradi).
3. License mode: **Trial** yoki **Fabric capacity**.

## 2. Itemlar (shu nomlar bilan yarating)
| Item | Nomi |
|---|---|
| Lakehouse | `lh_bronze` |
| Lakehouse | `lh_silver` |
| Lakehouse | `lh_gold` |
| Warehouse | `wh_urban_analytics` |
| Data pipeline | `pl_ingest_taxi` |
| Data pipeline | `pl_master` |
| Dataflow Gen2 | `df_openaq` |
| Dataflow Gen2 | `df_worldbank_gdp` |
| Dataflow Gen2 | `df_ecb_fx` |
| Notebook | `nb_config`, `nb_common` |
| Notebook | `nb_silver_taxi_trips`, `nb_silver_taxi_zones`, `nb_silver_air_quality`, `nb_silver_economy` |
| Notebook | `nb_gold_dimensions`, `nb_gold_facts` |
| Notebook | `nb_insights` |

> Lakehouse yaratishda **"Lakehouse schemas"** belgisini qo'ymang (oddiy `dbo` sxemasi kerak).

## 3. OpenAQ API kaliti
1. https://explore.openaq.org/register — ro'yxatdan o'ting.
2. Account settings → **API Key** ni nusxalang (Dataflow parametrida ishlatiladi).

## 4. HTTP connection (Taxi uchun)
**Settings → Manage connections and gateways → New → Cloud**
- Connection name: `conn_nyc_tlc`
- Connection type: **HTTP**
- Base URL: `https://d37ci6vzurychx.cloudfront.net/`
- Authentication: **Anonymous**

## 5. Ishga tushirish tartibi (birinchi marta)
1. `02_bronze` → pipeline va dataflowlarni yarating va bir marta ishga tushiring.
2. `03_silver` → notebooklarni ketma-ket ishga tushiring.
3. `04_gold` → `nb_gold_dimensions`, keyin `nb_gold_facts`.
4. `05_warehouse` → SQL skriptlarni raqam tartibida bajaring.
5. `06_orchestration` → `pl_master` va schedule.
6. `07_analytics` → insights notebook va Power BI.
