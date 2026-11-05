# DATUM — паспорт проекта

Обновлено: 2026-11-05.

## Назначение

Пошаговый данжен-кроулер от первого лица внутри самореплицирующейся мегаструктуры. **Ядро с октября 2026 — драфт-роглайт по Blue Prince:** строишь здание, выбирая комнату из трёх, и спускаешься по нему. Прототип в репозитории описывает прежнее ядро (v1) — он остаётся стендом рендера, звука и боя.

## Источник правды

| Вопрос | Где смотреть |
|---|---|
| Дизайн (механики, сюжет, гейты) | **`gdd/`** — `datum-gdd.md` v2.6, `datum-gates.md`, `datum-hub-graph.md` |
| Состояние и устройство кода | `docs/DATUM-handover.md` |
| Дизайн v1 | `docs/DATUM-design.md` — **устарел**, оставлен ради фикции, боя и архетипов |
| Звук | `docs/DATUM-sound-brief.md` |

## Стек

- HTML/JS (three.js r128), без сборщика. Исходник грузит three.js с cdnjs; сборка вшивает его из `build/vendor/three.min.js`, поэтому `dist/DATUM.html` работает без сети.
- Python-сборка `build/make.py` (проверка исходника + сборка `dist/DATUM.html`).
- Смоук-тест `build/datum_smoke.py` — headless Chrome, ошибки консоли + снимок HUD.
- Арт-скрипты: `datum_workers.py`, `datum_chars.py`, `datum_tex.py`.

## Структура

- `datum-prototype.html` — исходник прототипа.
- `build/make.py` — сборка; `dist/DATUM.html` — результат.
- `gdd/` — дизайн v2 (Obsidian-хранилище; в хранилище ShortGames виден как папка `DATUM`).
- `docs/` — handover, звук, дизайн v1.

## Запуск

```
py build\make.py
py build\datum_smoke.py
```

Затем открыть `dist/DATUM.html` в браузере.

## Статус

Прототип v1 работает и собран (2026-11-05, 10,4 МБ, без внешних ссылок). Дизайн v2 — на гейте 2; следующее — гейт 4 (`gdd/loops.md`, `gdd/progression.md`). Код, ассеты и кредиты по методу Рубана — только после гейта 6. GitHub public `Zeghreit/Datum`; начинать с `docs/DATUM-handover.md`.
