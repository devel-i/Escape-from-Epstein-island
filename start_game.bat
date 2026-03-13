@echo off
setlocal

if "%BUILD_DIR%"=="" set BUILD_DIR=build

cmake -S . -B %BUILD_DIR%
if errorlevel 1 exit /b %errorlevel%

cmake --build %BUILD_DIR% --config Release
if errorlevel 1 exit /b %errorlevel%

if exist %BUILD_DIR%\Release\escape_island.exe (
  %BUILD_DIR%\Release\escape_island.exe %*
) else (
  %BUILD_DIR%\escape_island.exe %*
)
