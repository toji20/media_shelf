# MediaShelf — домашняя медиатека

Десктопное приложение на Python + PySide6 (Qt). Каталог книг, фильмов и альбомов:
поиск, фильтр по типу, сортировка, добавление / изменение / удаление, описание и рейтинг.

## Запуск
```bash
pip install -r requirements.txt
python main.py
```

## Структура
- `main.py` — точка входа (класс `Application`)
- `models.py` — абстрактный `Entity`, `MediaItem` (`Book`, `Movie`, `Album`), `Library`, `SessionRecord`
- `custom_map.py` — собственный класс отображения вместо `dict`
- `storage.py` — сохранение данных (CSV) и отчёта о работе (`report.txt`)
- `widgets.py` — 14 переопределённых компонентов окна

## Отчёт
При закрытии приложения в `report.txt` добавляется строка сессии (login | time_in | time_out, формат `%d.%m.%Y %H:%M:%S`).
