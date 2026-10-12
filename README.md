<img width="1920" height="1080" alt="Снимок экрана 2026-10-12 191016" src="https://github.com/user-attachments/assets/07be85f7-0463-4153-9a5d-3c13a03e7691" />
<img width="1920" height="1080" alt="Снимок экрана 2026-10-12 191638" src="https://github.com/user-attachments/assets/5b9ea94f-f275-4c4a-a059-412c576674d8" />
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
