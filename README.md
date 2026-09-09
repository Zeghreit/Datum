# DATUM

Пошаговый данжен-кроулер от первого лица внутри самореплицирующейся мегаструктуры. Прототип — один HTML-файл, открывается в любом браузере.

**Начни с [docs/DATUM-handover.md](docs/DATUM-handover.md)** — состояние проекта, устройство конвейера и список уже пройденных граблей.

- Дизайн целиком: [docs/DATUM-design.md](docs/DATUM-design.md)
- Звуковое задание: [docs/DATUM-sound-brief.md](docs/DATUM-sound-brief.md)

## Сборка

```
py build/make.py
```

Проверяет исходник `datum-prototype.html` и собирает `dist/DATUM.html`.
Пересборка арта нужна только при смене картинок: `datum_workers.py`, `datum_chars.py`, `datum_tex.py`.


---

# Datum
Megastructure dungeon crawler
