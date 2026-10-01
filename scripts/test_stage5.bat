@echo off
rem =============================================================
rem  Этап 5. Дополнительные команды: touch, chmod, vfs-load.
rem  Закрывайте каждое окно командой exit для перехода дальше.
rem =============================================================
cd /d "%~dp0.."

echo.
echo === 1. Интерактивно: попробуйте touch, chmod, vfs-load ===
python -m src.main
echo.

echo === 2. Все режимы этапа 5 через стартовый скрипт ===
python -m src.main --script scripts\startup_stage5.txt
echo.

echo === 3. Команды этапа 5 на глубоком VFS ===
python -m src.main --vfs vfs_deep --script scripts\startup_stage5.txt
echo.

echo Все сценарии выполнены.
pause
