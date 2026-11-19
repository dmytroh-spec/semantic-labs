# Об'єднаний набір даних

`build_unified_data.py` поєднує каталог RDF із лабораторної 1 та семантичні
факти лабораторної 2. Канонічні ідентифікатори мають формат
`attraction/<slug>`; початкові назви й псевдоніми використовуються лише для
зіставлення.

Запуск із кореня репозиторію:

```powershell
python integration/build_unified_data.py
```

Результат: `data/unified_kyiv_tourism.json`.
