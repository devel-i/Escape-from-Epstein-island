# Побег с острова Эпштейна — Desktop 3D

Проект полностью переведён в **десктопную 3D-игру** на Python + Pygame.

## Что реализовано
- псевдо-3D рендеринг уровня (raycasting, вид от первого лица) с улучшенным освещением/туманом;
- градиентное небо, более выразительный пол и миникарта;
- управление: `WASD`/стрелки, мышь для обзора (сниженная чувствительность движения);
- взаимодействие с терминалами (`E`) и ввод ответов (`Enter`);
- 3 усложнённых терминала-головоломки (18+ и чёрный юмор в формулировках);
- выход открывается только после сбора всех ключей.

## Управление
- `W` / `S` — движение вперёд / назад
- `A` / `D` — шаг влево / вправо
- `←` / `→` — поворот
- `Мышь` — обзор
- `E` — взаимодействие с терминалом
- `Enter` — подтвердить ответ
- `Esc` — выход из игры

<<<<<<< 8fqa7b-codex/adapt-launch-for-multiple-platforms
## Важно про Python 3.14
На Python **3.14** пакет `pygame` часто пытается собираться из исходников и падает.
Используйте **`pygame-ce`** (он импортируется как обычный `pygame`).

## Запуск (Linux / macOS)
```bash
python3 -m pip install --only-binary=:all: pygame-ce
=======
## Зависимости по версии Python
- **Python 3.14+**: используйте `pygame-ce`
- **Python 3.13 и ниже**: используйте `pygame`

## Запуск (Linux / macOS)
```bash
# Python 3.14+
python3 -m pip install pygame-ce
# Python <=3.13
python3 -m pip install pygame

>>>>>>> main
python3 main.py
```

## Запуск (Windows PowerShell)
```powershell
<<<<<<< 8fqa7b-codex/adapt-launch-for-multiple-platforms
py -m pip install --only-binary=:all: pygame-ce
=======
py -m pip install pygame
>>>>>>> main
py main.py
```

## Запуск (Windows CMD)
```bat
<<<<<<< 8fqa7b-codex/adapt-launch-for-multiple-platforms
py -m pip install --only-binary=:all: pygame-ce
=======
REM Python 3.14+
py -m pip install pygame-ce
REM Python <=3.13
py -m pip install pygame

>>>>>>> main
py main.py
```

## Скрипты быстрого запуска
- Linux/macOS: `./start_game.sh`
- Windows: `start_game.bat`

<<<<<<< 8fqa7b-codex/adapt-launch-for-multiple-platforms
Скрипты сначала пробуют поставить `pygame-ce` из wheel, и только если это недоступно — переходят на `pygame<2.7` из wheel.
=======
Оба скрипта автоматически определяют версию Python и ставят нужный пакет (`pygame` или `pygame-ce`).
>>>>>>> main

## Быстрая проверка без окна (CI/smoke)
Кроссплатформенно (без ручной настройки `SDL_VIDEODRIVER`):

```bash
python3 main.py --headless-smoke 3
```

Для Windows:

```powershell
py main.py --headless-smoke 3
```
