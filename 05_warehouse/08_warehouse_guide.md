# 08. Warehouse sozlash

1. `wh_urban_analytics` ni oching → **New SQL query**.
2. Har bir faylni **alohida query**da, raqam tartibida bajaring:
   1. `01_create_schema.sql`
   2. `02_create_dimensions.sql`
   3. `03_create_facts.sql`
   4. `04_create_load_procedures.sql` — `GO` bilan ajratilgan bloklarni **birma-bir** belgilab (select) **Run** qiling
   5. `05_create_analytics_views.sql` — xuddi shunday, har bir `CREATE VIEW` blokini alohida
   6. `06_run_load_and_validate.sql` — birinchi yuklash va tekshiruv
   7. `07_create_security.sql` — email'ni o'zingizning tenant foydalanuvchingizga almashtiring
      (`DimBorough` 6-qadamda to'lgan bo'lishi kerak)

> Fabric SQL editor `GO` ni tanimasa — har bir blokni alohida bajaring.

## Qanday ishlaydi
- `gold.usp_reload_table` — maqsad jadval ustunlarini `INFORMATION_SCHEMA` dan oladi va
  `lh_gold.dbo.<source>` dan bir xil nomli ustunlarni `DELETE + INSERT` qiladi (bitta generic procedure — DRY).
  `TRUNCATE` ishlatilmaydi: foreign key ko'rsatgan jadvalni (`NOT ENFORCED` bo'lsa ham) truncate qilib bo'lmaydi.
- `lh_gold` shu workspace'da bo'lgani uchun warehouse unga 3-qismli nom bilan murojaat qila oladi.
- Primary/foreign key'lar `NOT ENFORCED` — Fabric Warehouse talabi, Power BI relationship'lari uchun metadata.

## Analitik view'lar → savollar
| View | Savol |
|---|---|
| `vw_MobilityAirCorrelation` (`daily_city`) | 1. Kunlik qatnov ↔ PM2.5/NO2 |
| `vw_MobilityAirCorrelation` (`hourly_borough`) | 2. Qaysi borough/kun vaqtida bog'liqlik kuchli |
| `vw_MonthlyRevenueUsdEur` | 3. Safar daromadi USD vs EUR, kurs ta'siri |
| `vw_YearlyMobilityEconomyEnvironment` | 4. O'sish ekologiya hisobigami |
