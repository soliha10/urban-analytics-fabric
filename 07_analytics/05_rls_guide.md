# 05. Row-Level Security (RLS)

## Maqsad
- **BoroughAnalyst** — faqat o'ziga biriktirilgan borough(lar) ma'lumotini ko'radi.
- **CityManager** — butun shahar ma'lumotini ko'radi.

## Sozlash
1. `05_warehouse/07_create_security.sql` orqali `gold.SecurityUserBorough` ga foydalanuvchi → borough yozing.
2. `sm_urban_analytics` → **Manage roles** → **New role**:
   - `BoroughAnalyst`: jadval `DimBorough`, **DAX editor** → `04_rls_roles.dax` dagi filter.
   - `CityManager`: jadval `DimBorough`, filter `TRUE ()`.
3. **Assign** → foydalanuvchi/guruhlarni rollarga qo'shing.
4. **Test as role** → `BoroughAnalyst` + *Other user* email bilan tekshiring.

## Filtr qanday tarqaladi
`DimBorough` → `DimZone` → `FactTaxiDaily`, va `DimBorough` → `FactAirQualityDaily` / `FactMobilityAirHourly`.
Bitta filtr barcha fact jadvallarni cheklaydi.

> Workspace **Admin/Member/Contributor** rollari RLS'ni chetlab o'tadi — analitiklarga faqat **Viewer**
> yoki hisobotga **Read** ruxsat bering.
