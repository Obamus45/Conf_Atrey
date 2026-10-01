@echo off
rem =============================================================
rem  Этап 2. Обработка ошибок параметров командной строки.
rem  В каждом сценарии эмулятор должен показать сообщение об
rem  ошибке в консоли и завершиться с кодом 1.
rem =============================================================
cd /d "%~dp0.."

echo === 1. --vfs: несуществующий путь ===
python -m src.main --vfs no_such_dir
echo Код возврата: %ERRORLEVEL%
echo.

echo === 2. --vfs: указан файл вместо директории ===
python -m src.main --vfs README.md
echo Код возврата: %ERRORLEVEL%
echo.

echo === 3. --script: несуществующий файл ===
python -m src.main --script no_such_script.txt
echo Код возврата: %ERRORLEVEL%
echo.

echo === 4. --script: указана директория вместо файла ===
python -m src.main --script demo
echo Код возврата: %ERRORLEVEL%
echo.

echo Все сценарии ошибок выполнены (все коды должны быть 1).
pause
