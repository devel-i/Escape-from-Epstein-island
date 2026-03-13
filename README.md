# Escape from Epstein Island — Modern C 3D

Проект полностью переписан на **C + raylib** с современным 3D-рендерингом:
- полноценная 3D-сцена (кубические стены, подсвеченные терминалы, объёмные объекты);
- динамичные эффекты (пульсация, глубина, градиенты, HUD);
- вопросы у терминалов без подсказки правильного ответа;
- спринт/выносливость, интерактивные терминалы, финальный выход.

## Управление
- `W / A / S / D` — движение
- `Shift` — спринт
- `Мышь` — обзор от первого лица
- `E` — взаимодействовать с терминалом
- `Enter` — проверить ответ
- `Esc` — выйти из ввода

## Сборка и запуск (Linux/macOS)
```bash
./start_game.sh
```

Или вручную:
```bash
cmake -S . -B build
cmake --build build -j
./build/escape_island
```

## Сборка под `.exe` (Windows)
```bat
start_game.bat
```

Или вручную:
```bat
cmake -S . -B build
cmake --build build --config Release
build\Release\escape_island.exe
```

## Зависимости
- `CMake >= 3.16`
- `raylib` (доступный для `find_package(raylib REQUIRED)`)

Пример с `vcpkg`:
```bat
vcpkg install raylib
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake
cmake --build build --config Release
```
