# 02. `pl_master` va refresh schedule

## Oqim
```
Ingest taxi files ──► Silver taxi trips ─┐
                 └──► Silver taxi zones ─┤
Refresh OpenAQ ─────► Silver air quality ┼──► Gold dimensions ──► Gold facts ──► Load warehouse star schema
Refresh WB GDP ──┐                       │
Refresh ECB FX ──┴──► Silver economy ────┘
```

## Yaratish
**A variant (JSON):** `pl_master` → **View JSON code** → `01_pl_master.json` ni joylashtiring va placeholderlarni almashtiring:
- `<PL_INGEST_TAXI_ID>`, `<DF_..._ID>`, `<NB_..._ID>`, `<WAREHOUSE_ID>` — har bir item ochilganda URL'dagi GUID
- `<WAREHOUSE_SQL_ENDPOINT>` — Warehouse → Settings → **SQL connection string**

**B variant (UI):** activity'larni qo'lda qo'shing:
| Activity turi | Nomi | Sozlama |
|---|---|---|
| Invoke pipeline | Ingest taxi files | `pl_ingest_taxi`, Wait on completion ✔ |
| Dataflow (x3) | Refresh OpenAQ / World Bank GDP / ECB FX | mos dataflow, Retry 1 |
| Notebook (x6) | Silver ... / Gold ... | mos notebook |
| Stored procedure | Load warehouse star schema | Warehouse `wh_urban_analytics`, `gold.usp_load_star_schema` |

Bog'lanishlarni (yashil **On success** strelkalar) yuqoridagi sxema bo'yicha torting.

## Schedule
`pl_master` → **Schedule** → On:
- Repeat: **Daily**, Time: **03:00**, Time zone: **(UTC+05:00) Toshkent**
- Taxi fayllar oyda bir marta chiqadi — pipeline mavjud fayllarni o'tkazib yuboradi, shuning uchun kunlik ishga tushirish arzon.
- OpenAQ ma'lumotlari soatlik yangilanishi kerak bo'lsa: `df_openaq` uchun alohida **hourly** schedule qo'ying.

## Monitoring
- **Monitor hub** → pipeline run'lari, davomiylik, xatolar.
- Har bir notebook `write_table` dan keyin qatorlar sonini chiqaradi — run output'da ko'rinadi.
- Ixtiyoriy: oxiriga **Office 365 Outlook** activity'ni **On failure** ga ulab, xato bo'lganda email yuboring.
