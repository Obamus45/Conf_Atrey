@echo off
rem =============================================================
rem  Этап 2. Тест всех параметров командной строки эмулятора.
rem  Каждый запуск открывает окно эмулятора: закройте его
rem  командой exit, чтобы перейти к следующему сценарию.
rem =============================================================
cd /d "%~dp0.."

echo.
echo === 1. Без параметров (значения по умолчанию) ===
python -m src.main
echo.

echo === 2. --vfs: нестандартная директория VFS ===
python -m src.main --vfs vfs_sample
echo.

echo === 3. --script: стартовый скрипт ===
python -m src.main --script scripts\startup_basic.txt
echo.

echo === 4. Все параметры одновременно ===
python -m src.main --vfs vfs_sample --script scripts\startup_basic.txt
echo.

echo === 5. --demo: стандартный стартовый скрипт ===
python -m src.main --demo
echo.

echo Все сценарии выполнены.
pause
