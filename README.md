# Побег с острова Эпштейна — 3D версия

По запросу убрана 2D-концепция: теперь в репозитории только **3D-игра** (raycasting) в двух реализациях на разных языках.

## Вариант 1: Desktop 3D (Python + Pygame)

### Что есть
- псевдо-3D рендеринг уровня (raycasting);
- управление: `WASD` / стрелки, мышь — обзор;
- взаимодействие `E` с терминалами;
- 3 головоломки для сбора ключей;
- победа только после открытия выхода.

### Запуск
```bash
python3 -m pip install pygame
python3 main.py
```

## Вариант 2: Web 3D (JavaScript + Canvas)

### Что есть
- raycasting-рендеринг в браузере;
- управление: `WASD`/стрелки, `Q/E` — поворот;
- сбор 3 карт-ключей;
- выход открывается после выполнения условий.

### Запуск
```bash
cd web_game
python3 -m http.server 8000
```
Открыть: <http://localhost:8000>

## Smoke-test desktop без окна
```bash
SDL_VIDEODRIVER=dummy python3 main.py --headless-smoke 3
```
