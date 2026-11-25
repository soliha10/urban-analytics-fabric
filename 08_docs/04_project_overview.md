# Loyiha nima uchun va natijada nima bo'lishi kerak

## 1. Maqsad

Shahar ma'murlari uchta savolga javob izlaydi:
- transport havoni ifloslantiryaptimi?
- taksi biznesi qancha pul ishlab topyapti?
- iqtisodiy o'sish ekologiya hisobiga bo'lyaptimi?

Bu savollarga javob beradigan ma'lumotlar uch xil joyda, uch xil formatda turadi:

| Soha | Manba | Format | Nima beradi |
|---|---|---|---|
| Mobillik | NYC Taxi (TLC) | Oylik Parquet fayllar | Har bir safar: vaqt, zona, masofa, narx |
| Ekologiya | OpenAQ API | JSON, sahifalab olinadi | Soatlik PM2.5, NO2, O3 o'lchovlari |
| Iqtisod | World Bank va ECB | JSON va CSV | Yillik GDP va kunlik USD/EUR kursi |

Loyiha maqsadi shu uch manbani **bitta platformaga yig'ish, tozalash va bir-biriga bog'lash**.
Shundan keyin "taksi qatnovi ko'p bo'lgan kuni havo yomonroqmi?" degan savolga bitta so'rov bilan javob olish mumkin bo'ladi.

Ikkinchi maqsad o'quv maqsadi: Microsoft Fabric'ning to'liq stack'ini (Pipeline, Dataflow, Lakehouse,
Notebook, Warehouse, Power BI) haqiqiy ochiq ma'lumotlarda ishlata olishni ko'rsatish.

## 2. Ma'lumot qanday yo'l bosadi (medallion arxitektura)

```
Internet ──► BRONZE ──► SILVER ──► GOLD ──► WAREHOUSE ──► POWER BI
           (xom)     (toza)    (agregat)  (star schema)  (dashboard)
```

### Bronze — "hech narsani o'zgartirmay saqla"
- Ma'lumot manbadan qanday kelgan bo'lsa, shunday saqlanadi.
- Keyin xato topilsa, internetdan qayta yuklamasdan shu yerdan qayta ishlash mumkin.
- **Natija:** `lh_bronze` da 3 ta taksi Parquet fayli (2024-01…03), zonalar CSV fayli va 3 ta jadval (OpenAQ, GDP, FX).

### Silver — "tozala va standartlashtir"
- Noto'g'ri yozuvlar olib tashlanadi: manfiy narx, 0 daqiqalik yoki 10 soatlik safar, NYC tashqarisidagi stansiya.
- Dublikatlar o'chiriladi.
- Turli manbalar bitta tilga keltiriladi:
  - ustun nomlari bir xil bo'ladi;
  - o'lchov birliklari birlashtiriladi (NO2/O3: ppm va µg/m³ → ppb);
  - vaqt atributlari qo'shiladi: soat, dam olish kunimi, `morning_rush` kabi kun vaqti.
- **Natija:** `lh_silver` da 5 ta toza Delta jadval.

### Gold — "savolga moslab yig'"
- Millionlab alohida safar kunlik va soatlik yig'indilarga aylantiriladi.
- Har bir kunning daromadi o'sha kungi kurs bo'yicha EUR'ga o'giriladi.
- ECB dam olish kunlari kurs e'lon qilmaydi — bunday kunlar oldingi ish kunining kursi bilan to'ldiriladi.
- **Natija:** `lh_gold` da 5 ta dimension va 3 ta fact jadval.

### Warehouse — "hisobot uchun rasmiy model"
- Gold jadvallari star schema ko'rinishida yuklanadi: markazda fact'lar (raqamlar),
  atrofida dimension'lar (sana, zona, borough, kurs, GDP).
- To'rtta savolga javob beradigan tayyor view'lar shu yerda.

### Power BI — "qaror qabul qiluvchi ko'radigan joy"
- 4 sahifali dashboard: Mobility, Air Quality, Mobility vs Air, Economic Impact.
- Ochiq havola (login shart emas): https://app.fabric.microsoft.com/view?r=eyJrIjoiMWI0MzI3NjQtYjkwOC00NWIxLWEzNDAtYWFiZWY0ZjVlODljIiwidCI6ImNkNjgxMGVmLWFiYzYtNGZjMS1hYjA1LWNmYzhhMTliNzJjNSIsImMiOjEwfQ%3D%3D
- RLS (ixtiyoriy) loyihalangan: `07_analytics/04_rls_roles.dax`, lekin modelda yoqilmagan.

## 3. Yakunda qo'lda nima bo'lishi kerak

| # | Deliverable | Tekshiruvchi nimani ko'radi |
|---|---|---|
| 1 | Lakehouse'lar | `lh_bronze`, `lh_silver`, `lh_gold` to'lgan, uchala soha ma'lumoti bor |
| 2 | Avtomatik ingestion | `pl_ingest_taxi`, 3 ta Dataflow Gen2 va `pl_master` Monitor hub'da yashil (Succeeded) |
| 3 | Warehouse | `wh_urban_analytics.gold` da 8 ta jadval va 5 ta view; `06_run_load_and_validate.sql` qatorlar sonini ko'rsatadi |
| 4 | Vizualizatsiya | `nb_insights` grafiklari va 4 sahifali Power BI hisoboti (ochiq havola bilan) |
| 5 | Governance | Kunlik 03:00 schedule, Lineage view'da to'liq zanjir; RLS (ixtiyoriy) loyihalangan |
| 6 | Hujjatlar | `08_docs/`: data dictionary, lineage diagramma, governance siyosati, shu overview |

**Muvaffaqiyat mezoni:** `pl_master` ni bir marta bosganda butun zanjir
(yuklash → tozalash → agregatsiya → warehouse) inson aralashuvisiz oxirigacha o'tadi,
dashboard esa yangi ma'lumotni ko'rsatadi.

## 4. To'rt savol va javob qanday ko'rinishda bo'ladi

Quyida natijaning shakli, uni o'qish usuli va Fabric'da olingan haqiqiy raqamlar (2024-01…03).

| Ko'rsatkich | Qiymat |
|---|---|
| Safarlar (Silver, tozalangandan keyin) | 9,172,303 — kuniga o'rtacha 100.79K |
| O'rtacha narx / safar boshiga daromad | $18.68 / $27.48 |
| Kunlik korrelyatsiya, trips ↔ NO2 / O3 / PM2.5 | 0.166 / 0.126 / 0.124 |
| Eng kuchli soatlik segment | Bronx `evening_rush` O3 0.288, Manhattan `morning_rush` NO2 0.223 |
| Safar boshiga daromad USD / EUR (kurs) | Yanvar 27.31 / 25.04 (1.091), Fevral 27.21 / 25.20 (1.080), Mart 27.83 / 25.62 (1.086) |
| Jami daromad | $252.02M = €232.10M, FX impact €26.85K |

Power BI'dagi `Trips vs Pollutant Correlation` kartasi slicer tanlanmaganda 0.37 ko'rsatadi — bu barcha
ifloslantiruvchilar o'rtachasi bo'yicha; har bir ifloslantiruvchi uchun aniq qiymatni slicer orqali tanlab ko'ring.

### 1) Kunlik qatnov havo sifati bilan qanday bog'liq?
- **Qayerda:** `gold.vw_MobilityAirCorrelation`, `analysis_level = 'daily_city'`.
- **Natija:** har bir yil va har bir ifloslantiruvchi uchun Pearson `r` soni (−1 dan +1 gacha).
- **O'qish:**
  - `r` ≥ +0.5 — qatnov ko'p kunlari havo sezilarli yomonroq;
  - `r` ≈ 0 — kunlik darajada bog'liqlik yo'q.
- NO2 transport chiqindisiga PM2.5 dan ko'ra bevosita bog'liq, shuning uchun NO2 da bog'liqlik kuchliroq chiqishi kutiladi.

### 2) Qaysi joy va vaqtda bog'liqlik eng kuchli?
- **Qayerda:** o'sha view, `analysis_level = 'hourly_borough'` (segment: `Manhattan | evening_rush`).
- **Natija:** borough × kun vaqti kombinatsiyalari `|r|` bo'yicha tartiblangan ro'yxat.
- Faqat `sample_size` ≥ 30 bo'lgan qatorlarga ishoning — kam kuzatuvli segmentlar tasodifiy natija beradi.

### 3) Bir safarning daromadi USD va EUR'da qancha, kurs qanday ta'sir qiladi?
- **Qayerda:** `gold.vw_MonthlyRevenueUsdEur` va Power BI'dagi `[FX Impact EUR]`.
- **Natija:** har oy uchun safar boshiga USD daromad, EUR daromad va o'rtacha kurs.
- **O'qish:** USD daromad o'zgarmasa-yu EUR daromad o'zgarsa — bu faqat kurs ta'siri.
  `FX Impact EUR` = haqiqiy kurs bo'yicha EUR − davr o'rtacha kursi bo'yicha EUR.

### 4) O'sish ekologiya hisobigami?
- **Qayerda:** `gold.vw_YearlyMobilityEconomyEnvironment`.
- **Natija:** har yil uchun qatnov soni, daromad, PM2.5 va NO2 o'rtachasi, AQSh GDP'si va o'sish foizlari.
- **O'qish:**
  - qatnov va GDP o'sib, ifloslanish ham o'ssa — "ha, ekologiya hisobiga";
  - ifloslanish tushsa yoki o'zgarmasa — "o'sish ekologiyaga zarar keltirmayapti".
- Taksi va havo ma'lumoti F2 capacity va kredit tejash uchun 3 oy (2024-01…03) bilan cheklangan,
  shuning uchun yillik taqqoslash hozir bitta yilni ko'rsatadi (GDP esa 2000–2025). Ko'p yillik xulosa uchun davrni kengaytiring
  (`nb_config` dagi `ANALYSIS_START` va `pl_ingest_taxi` dagi `months`).

## 5. Himoyada aytish kerak bo'lgan cheklovlar
- **Korrelyatsiya sababni isbotlamaydi.** Ob-havo (shamol, harorat) ham ifloslanishga ta'sir qiladi,
  lekin bu scope'ga kirmagan — topshiriqda u keyingi kengaytirish sifatida tilga olingan.
- **Borough taxminiy aniqlanadi.** Stansiya eng yaqin borough markaziga biriktiriladi.
- **OpenAQ qamrovi notekis.** Stansiyalar har xil to'liqlikda ishlaydi — buni `sensor_count` va `reading_count` ko'rsatadi.
