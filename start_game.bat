@echo off
setlocal

set PYTHON_BIN=%PYTHON_BIN%
if "%PYTHON_BIN%"=="" set PYTHON_BIN=py

REM 1) Prefer pygame-ce wheel (required/recommended for Python 3.14+).
REM 2) Fallback to pygame wheel for older environments.
%PYTHON_BIN% -m pip install --only-binary=:all: pygame-ce
if errorlevel 1 (
    %PYTHON_BIN% -m pip install --only-binary=:all: "pygame<2.7"
)
if errorlevel 1 exit /b %errorlevel%

%PYTHON_BIN% main.py %*
