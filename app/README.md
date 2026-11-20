# Kyiv Semantic Guide API

API читає `data/unified_kyiv_tourism.json` і не дублює дані лабораторних.

## Запуск

```powershell
python -m pip install -r app/requirements.txt
python -m uvicorn app.main:app --reload
```

Документація OpenAPI: `http://127.0.0.1:8000/docs`.
Вебінтерфейс: `http://127.0.0.1:8000/`.

## Методи

- `GET /api/health` — стан і кількість сутностей;
- `GET /api/categories` — категорії;
- `GET /api/attractions` — каталог, пошук та фільтри;
- `GET /api/attractions/{id}` — детальна інформація і семантичні факти;
- `GET /api/routes` — маршрути з координатами впорядкованих зупинок;
- `GET /api/routes/{id}` — детальна інформація про маршрут, відстань і тривалість.

Параметри каталогу: `q`, `category`, `free_only`, `min_rating`.

## Тестування

```powershell
python -m unittest discover -s app/tests -v
```
