# Data Lineage

```mermaid
flowchart LR
    subgraph Sources
        TLC[NYC TLC<br/>Parquet + CSV]
        OAQ[OpenAQ v3 API<br/>JSON]
        WB[World Bank API<br/>JSON]
        ECB[ECB API<br/>CSV]
    end

    subgraph Bronze[lh_bronze]
        BT[Files/taxi/yellow]
        BZ[Files/taxi/reference]
        BA[bronze_openaq_hourly]
        BG[bronze_worldbank_gdp]
        BF[bronze_ecb_fx]
    end

    subgraph Silver[lh_silver]
        ST[silver_taxi_trips]
        SZ[silver_taxi_zones]
        SA[silver_air_quality]
        SF[silver_fx_rates]
        SG[silver_gdp]
    end

    subgraph Gold[lh_gold]
        DD[dim_date]
        DB[dim_borough]
        DZ[dim_zone]
        DF[dim_fx]
        DG[dim_gdp]
        FT[fact_taxi_daily]
        FA[fact_air_quality_daily]
        FH[fact_mobility_air_hourly]
    end

    WH[(wh_urban_analytics<br/>gold star schema + views)]
    PBI[Power BI<br/>sm_urban_analytics / rpt_urban_analytics]
    PUB[Public report<br/>sm_urban_analytics_import / rpt_urban_analytics_public]

    TLC -- pl_ingest_taxi --> BT & BZ
    OAQ -- df_openaq --> BA
    WB -- df_worldbank_gdp --> BG
    ECB -- df_ecb_fx --> BF

    BT -- nb_silver_taxi_trips --> ST
    BZ -- nb_silver_taxi_zones --> SZ
    BA -- nb_silver_air_quality --> SA
    BG -- nb_silver_economy --> SG
    BF -- nb_silver_economy --> SF

    SZ -- nb_gold_dimensions --> DB & DZ
    SF -- nb_gold_dimensions --> DF
    SG -- nb_gold_dimensions --> DG
    ST -- nb_gold_facts --> FT & FH
    SA -- nb_gold_facts --> FA & FH
    DF --> FT

    Gold -- usp_load_star_schema --> WH
    WH -- Direct Lake --> PBI
    WH -- Import refresh --> PUB
```

`rpt_urban_analytics_public` is a clone of the main report bound to an Import-mode copy of the model, because
Publish to web does not accept Direct Lake models (`07_analytics/08_nb_public_model.py`).

## Orchestration
`pl_master` (daily 03:00 UTC+05:00, schedule configured; switched off while the capacity is paused) runs every arrow above in dependency order — see `06_orchestration/02_orchestration_guide.md`.

## Purview lineage
Fabric captures item-level lineage automatically. Open the workspace → **Lineage view** to see
pipelines → lakehouses → notebooks → warehouse → semantic model → report. With Microsoft Purview
connected to the tenant, the same graph appears in the Purview Data Map / Unified Catalog.
