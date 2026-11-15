# 02. `pl_ingest_taxi` pipeline'ni yaratish

Pipeline NYC TLC saytidan oylik Parquet fayllarni `lh_bronze/Files/taxi/yellow/` ga,
zonalar lug'atini `lh_bronze/Files/taxi/reference/` ga yuklaydi. Fayl allaqachon bo'lsa — o'tkazib yuboradi.

## A variant — JSON orqali (tez)
1. `pl_ingest_taxi` pipeline'ni oching → yuqorida **{ } View JSON code** (yoki *Edit JSON*).
2. `01_pl_ingest_taxi.json` mazmunini to'liq joylashtiring.
3. Placeholderlarni almashtiring:
   - `<WORKSPACE_ID>` — brauzer URL'idagi `/groups/<ID>/`
   - `<LH_BRONZE_ID>` — `lh_bronze` ochilganda URL'dagi `/lakehouses/<ID>`
   - `<HTTP_CONNECTION_ID>` — *Manage connections* → `conn_nyc_tlc` → Settings → Connection ID
4. **Save → Run**.

## B variant — UI orqali (JSON ishlamasa)
1. **Parameters** tab → `months` (Array) → JSON dagi `defaultValue` ro'yxati.
2. **Copy data** activity → nomi `Copy taxi zone lookup`
   - Source: connection `conn_nyc_tlc`, Relative URL `misc/taxi_zone_lookup.csv`, format **Binary**
   - Destination: Lakehouse `lh_bronze`, Root folder **Files**, path `taxi/reference/taxi_zone_lookup.csv`, format **Binary**
3. **ForEach** → nomi `For each taxi month`, Items: `@pipeline().parameters.months`, Batch count `4`.
4. ForEach ichida:
   - **Get Metadata** `Check month file exists` → `lh_bronze` Files, folder `taxi/yellow`,
     file `@concat('yellow_tripdata_', item(), '.parquet')`, Field list: **Exists**.
   - **If Condition** `If month file missing` → `@not(activity('Check month file exists').output.exists)`
   - True ichida **Copy data** `Copy taxi month`:
     - Source relative URL: `@concat('trip-data/yellow_tripdata_', item(), '.parquet')`, Binary
     - Destination: `lh_bronze` Files → `taxi/yellow` / `@concat('yellow_tripdata_', item(), '.parquet')`, Binary
     - Settings → Retry `2`.

## Tekshirish
`lh_bronze` → **Files/taxi/yellow** da 3 ta `.parquet` (2024-01…03), **Files/taxi/reference** da `taxi_zone_lookup.csv` bo'lishi kerak.
