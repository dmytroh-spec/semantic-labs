# Kyiv Semantic Guide API

API читає `data/unified_kyiv_tourism.json` і не дублює дані лабораторних.

## Запуск

```powershell
python -m pip install -r app/requirements.txt
python -m uvicorn app.main:app --reload
```

Документація OpenAPI: `http://127.0.0.1:8000/docs`.

## Методи

- `GET /api/health` — стан і кількість сутностей;
- `GET /api/categories` — категорії;
- `GET /api/attractions` — каталог, пошук та фільтри;
- `GET /api/attractions/{id}` — детальна інформація і семантичні факти;
- `GET /api/routes` — маршрути з координатами впорядкованих зупинок.

Параметри каталогу: `q`, `category`, `free_only`, `min_rating`.
