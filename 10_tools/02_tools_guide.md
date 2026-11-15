# 02. Lokal yordamchi skriptlar

Ikkala skript ham **sizning kompyuteringizda** ishlaydi, Fabric'da emas.

## O'rnatish (bir marta)
`03_local_smoke_test.py` uchun **Python 3.9–3.12** va **Java 17** kerak (PySpark 3.5 Python 3.13+ da ishlamaydi).
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r 10_tools/requirements.txt
```
`01_py_to_ipynb.py` uchun hech narsa o'rnatish shart emas (standart Python 3.8+).

## `01_py_to_ipynb.py` — `.py` → `.ipynb`
`.py` notebook manbalarini Fabric'ga import qilinadigan `.ipynb` fayllarga aylantiradi va `09_notebooks_ipynb/` ga yozadi.
```bash
python3 10_tools/01_py_to_ipynb.py
```
- `# %%` qatori yangi cell boshlanishini bildiradi (marker cell'ga kirmaydi).
- Notebook nomi `NOTEBOOK_SOURCES` dagi kalit — Fabric'dagi nom bilan bir xil bo'lishi shart.
- Yangi notebook qo'shsangiz, `NOTEBOOK_SOURCES` ga bitta qator qo'shing.

## `03_local_smoke_test.py` — notebooklarni lokal tekshirish
Barcha PySpark notebooklarni (Silver → Gold → Insights) kichik sun'iy ma'lumotda,
OneLake o'rniga vaqtinchalik lokal papkada ishga tushiradi va natijani tekshiradi.
```bash
python 10_tools/03_local_smoke_test.py
```
Kutilgan oxirgi qator:
```
12/12 checks passed. Local lake: /var/folders/.../fabric_smoke_xxxx
```
- Opechatka yoki xato bo'lsa — traceback qaysi fayl va qatorda ekanini ko'rsatadi.
- Tekshiradi: barcha gold jadvallar to'lgan, birliklar standartlashgan, NYC tashqarisidagi stansiya va
  noto'g'ri safarlar olib tashlangan, FX kursi har kun uchun to'ldirilgan.
- Fabric'ga xos qismlar (OneLake, Delta, `notebookutils`) lokal muqobil bilan almashtiriladi —
  shuning uchun bu test Fabric'dagi birinchi ishga tushirishni to'liq almashtirmaydi.
