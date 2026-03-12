# Побег с острова Эпштейна — Desktop 3D

Проект — десктопная 3D-игра на Python + Pygame (raycasting, вид от первого лица).

## Актуальное состояние
- управление: `WASD`/стрелки + мышь;
- сниженная скорость шага (движение более плавное);
- терминалы-головоломки (`E`, ввод ответа, `Enter`);
- выход открывается после прохождения всех терминалов;
- улучшенный рендер: туман/освещение, фон и миникарта.

## Управление
- `W` / `S` — движение вперёд / назад
- `A` / `D` — шаг влево / вправо
- `←` / `→` — поворот
- `Мышь` — обзор
- `E` — взаимодействие с терминалом
- `Enter` — подтвердить ответ
- `Esc` — выход из игры

## Python 3.14+
На Python 3.14 рекомендуется использовать `pygame-ce` (импортируется как `pygame`).

## Запуск (Linux / macOS)
```bash
python3 -m pip install --only-binary=:all: pygame-ce
python3 main.py
```

## Запуск (Windows PowerShell/CMD)
```powershell
py -m pip install --only-binary=:all: pygame-ce
py main.py
```

## Скрипты быстрого запуска
- Linux/macOS: `./start_game.sh`
- Windows: `start_game.bat`

Скрипты сначала ставят `pygame-ce` (wheel), а если недоступно — пробуют `pygame<2.7` (wheel).

## Smoke-проверка без окна
```bash
python3 main.py --headless-smoke 3
```
Windows:
```powershell
py main.py --headless-smoke 3
```
