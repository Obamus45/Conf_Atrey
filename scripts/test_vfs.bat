@echo off
rem =============================================================
rem  Этап 3. Тест эмулятора с различными вариантами VFS:
rem  минимальный, несколько файлов, не менее 3 уровней вложенности.
rem  Закрывайте каждое окно командой exit для перехода дальше.
rem =============================================================
cd /d "%~dp0.."

echo.
echo === 1. Минимальный VFS: vfs_minimal (один файл) ===
python -m src.main --vfs vfs_minimal
echo.

echo === 2. Несколько файлов: vfs_multi ===
python -m src.main --vfs vfs_multi
echo.

echo === 3. Не менее 3 уровней: vfs_deep ===
python -m src.main --vfs vfs_deep
echo.

echo === 4. VFS по умолчанию + полный стартовый скрипт ===
python -m src.main --script scripts\startup_full.txt
echo.

echo === 5. Все параметры: --vfs и --script вместе ===
python -m src.main --vfs vfs_deep --script scripts\startup_full.txt
echo.

echo === 6. Ошибка: несуществующий путь VFS ===
python -m src.main --vfs no_such_dir
echo Код возврата: %ERRORLEVEL%
echo.

echo Все сценарии выполнены.
pause
