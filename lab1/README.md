# Лабораторна робота 1 — RDF і SPARQL для туризму в Києві

Проєкт будує RDF-граф туристичних пам'яток і тематичних маршрутів Києва. Граф серіалізується у Turtle та JSON-LD, доповнюється вручну, візуалізується і досліджується п'ятьма SPARQL-запитами.

## Встановлення і запуск

```powershell
python -m pip install -r requirements.txt
python src/create_kyiv_graph.py
python src/explore_graph.py
python src/execute_queries.py
python src/fetch_wikidata.py
python src/draw_graph.py
python src/validate_project.py
python -m unittest discover -s tests -v
```

Запит до Wikidata потребує мережі. Якщо сервіс недоступний, решта лабораторної продовжує працювати з локальними `owl:sameAs`-зв'язками.

## Основні результати

- `data/kyiv_graph_generated.ttl` — автоматично сформований граф;
- `data/kyiv_graph.ttl` — граф після ручного доповнення;
- `data/kyiv_graph.jsonld` — друга RDF-серіалізація;
- `data/kyiv_manual_additions.ttl` — ручні доповнення графа;
- `output/sparql_results.md` — результати локальних SPARQL-запитів;
- `output/wikidata_kyiv.json` — результат зовнішнього запиту;
- `output/kyiv_tourism_graph.png` — візуалізація;
- `output/validation_report.txt` — аудит вимог лабораторної.

## Модель

Типи сутностей: `Country`, `City`, `Attraction`, `AttractionType`, `TouristRoute`. Основні зв'язки: `locatedInCity`, `locatedInCountry`, `hasAttractionType`, `includesAttraction`, `nextStop`. Реальні сутності пов'язані з Wikidata через `owl:sameAs`.

