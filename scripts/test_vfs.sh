#!/usr/bin/env bash
# =============================================================
#  Этап 3. Тест эмулятора с различными вариантами VFS:
#  минимальный, несколько файлов, не менее 3 уровней вложенности.
#  Закрывайте каждое окно командой exit для перехода дальше.
# =============================================================
cd "$(dirname "$0")/.."

echo
echo "=== 1. Минимальный VFS: vfs_minimal (один файл) ==="
python3 -m src.main --vfs vfs_minimal
echo

echo "=== 2. Несколько файлов: vfs_multi ==="
python3 -m src.main --vfs vfs_multi
echo

echo "=== 3. Не менее 3 уровней: vfs_deep ==="
python3 -m src.main --vfs vfs_deep
echo

echo "=== 4. VFS по умолчанию + полный стартовый скрипт ==="
python3 -m src.main --script scripts/startup_full.txt
echo

echo "=== 5. Все параметры: --vfs и --script вместе ==="
python3 -m src.main --vfs vfs_deep --script scripts/startup_full.txt
echo

echo "=== 6. Ошибка: несуществующий путь VFS ==="
python3 -m src.main --vfs no_such_dir
echo "Код возврата: $?"
echo

echo "Все сценарии выполнены."
