# 06. Dataflow Gen2 larni yaratish

Har bir dataflow — **bitta query**. Kodni **Advanced editor** ga to'liq joylashtirasiz.

| Fayl | Dataflow | Query nomi | Destination jadval (`lh_bronze`) |
|---|---|---|---|
| `03_df_openaq.pq` | `df_openaq` | `openaq_hourly` | `bronze_openaq_hourly` |
| `04_df_worldbank_gdp.pq` | `df_worldbank_gdp` | `worldbank_gdp` | `bronze_worldbank_gdp` |
| `05_df_ecb_fx.pq` | `df_ecb_fx` | `ecb_fx` | `bronze_ecb_fx` |

## Umumiy qadamlar (har biri uchun)
1. Workspace → **New item → Dataflow Gen2** → nom bering.
2. **Get data → Blank query** → **Advanced editor** → `.pq` fayl mazmunini joylashtiring → OK.
3. Query nomini jadvaldagidek o'zgartiring.
4. Ulanish so'ralsa: **Configure connection** → Authentication **Anonymous**, Privacy level **Public**.
5. Pastki o'ng burchak → **Data destination (+) → Lakehouse** → `lh_bronze` → **New table** → nomi jadvaldagidek.
6. Update method: **Replace**, column mapping'ni tasdiqlang → **Save settings**.
7. **Publish** (yoki *Save & run*).

## `df_openaq` uchun qo'shimcha
1. Query yaratishdan **oldin**: **Home → Manage parameters → New parameter**
   - Name: `OpenAQApiKey`, Type: **Text**, Current value: sizning OpenAQ API kalitingiz.
2. Parameter query'da **Enable load / staging** o'chirilgan bo'lsin (destination faqat `openaq_hourly` da).
3. Birinchi refresh ~10–20 daqiqa davom etadi (har bir so'rov orasida 1 soniya pauza — rate limit uchun).

## Tekshirish
`lh_bronze` → **Tables** da 3 ta jadval: `bronze_openaq_hourly`, `bronze_worldbank_gdp`, `bronze_ecb_fx`.
