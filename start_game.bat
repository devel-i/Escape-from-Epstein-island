@echo off
py -m pip install pygame
if errorlevel 1 exit /b %errorlevel%
py main.py %*
