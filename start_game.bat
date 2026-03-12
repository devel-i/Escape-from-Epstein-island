@echo off
set PYTHON_BIN=%PYTHON_BIN%
if "%PYTHON_BIN%"=="" set PYTHON_BIN=py

%PYTHON_BIN% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 14) else 1)"
if errorlevel 1 (
    %PYTHON_BIN% -m pip install pygame
) else (
    %PYTHON_BIN% -m pip install pygame-ce
)
if errorlevel 1 exit /b %errorlevel%

%PYTHON_BIN% main.py %*
