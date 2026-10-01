@echo off
rem Запуск эмулятора (вариант 26, этап 1).
rem Все аргументы передаются в приложение, например: run.bat --demo
cd /d "%~dp0"
python -m src.main %*
