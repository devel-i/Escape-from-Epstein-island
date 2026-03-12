# Побег с острова Эпштейна — Desktop 3D

Проект полностью переведён в **десктопную 3D-игру** на Python + Pygame.

## Что реализовано
- псевдо-3D рендеринг уровня (raycasting, вид от первого лица);
- управление: `WASD`/стрелки, мышь для обзора;
- взаимодействие с терминалами (`E`) и ввод ответов (`Enter`);
- 3 терминала-головоломки, прогресс по ключам;
- выход открывается только после сбора всех ключей.

## Управление
- `W` / `S` — движение вперёд / назад
- `A` / `D` — шаг влево / вправо
- `←` / `→` — поворот
- `Мышь` — обзор
- `E` — взаимодействие с терминалом
- `Enter` — подтвердить ответ
- `Esc` — выход из игры

## Запуск (Linux / macOS)
```bash
python3 -m pip install pygame
python3 main.py
```

## Запуск (Windows PowerShell)
```powershell
py -m pip install pygame
py main.py
```

## Запуск (Windows CMD)
```bat
py -m pip install pygame
py main.py
```

## Скрипты быстрого запуска
- Linux/macOS: `./start_game.sh`
- Windows: `start_game.bat`

## Быстрая проверка без окна (CI/smoke)
Кроссплатформенно (без ручной настройки `SDL_VIDEODRIVER`):

```bash
python3 main.py --headless-smoke 3
```

Для Windows:

```powershell
py main.py --headless-smoke 3
```
