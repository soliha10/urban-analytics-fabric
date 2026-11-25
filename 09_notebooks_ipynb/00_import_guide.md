# 00. Notebooklarni .ipynb orqali import qilish

`03_silver`, `04_gold`, `07_analytics` dagi `.py` fayllarning tayyor `.ipynb` versiyasi.
Kod bir xil — qo'lda cell-ma-cell ko'chirish o'rniga shu yo'lni ishlatsangiz bo'ladi.

## Import
1. Workspace `ws_urban_analytics` → **Import → Notebook → From this computer**.
2. Shu papkadagi **11 ta `.ipynb` faylning hammasini birdaniga** tanlang → **Upload**.
3. Notebook nomlari fayl nomidan olinadi (`nb_config`, `nb_common`, ...) — **nomini o'zgartirmang**,
   `%run nb_config` / `%run nb_common` shu nomlarga tayanadi.

## Importdan keyin
1. Har bir notebookni oching → chap panel **Lakehouses → Add** → `lh_silver` (default).
2. Kernel **PySpark (Python)** ekanini tekshiring.
3. Ishga tushirish tartibi `03_silver/07_notebooks_guide.md` dagidek.

| Fayl | Manba |
|---|---|
| `nb_config.ipynb` | `03_silver/01_nb_config.py` |
| `nb_common.ipynb` | `03_silver/02_nb_common.py` |
| `nb_silver_taxi_trips.ipynb` | `03_silver/03_nb_silver_taxi_trips.py` |
| `nb_silver_taxi_zones.ipynb` | `03_silver/04_nb_silver_taxi_zones.py` |
| `nb_silver_air_quality.ipynb` | `03_silver/05_nb_silver_air_quality.py` |
| `nb_silver_economy.ipynb` | `03_silver/06_nb_silver_economy.py` |
| `nb_gold_dimensions.ipynb` | `04_gold/01_nb_gold_dimensions.py` |
| `nb_gold_facts.ipynb` | `04_gold/02_nb_gold_facts.py` |
| `nb_insights.ipynb` | `07_analytics/01_nb_insights.py` |
