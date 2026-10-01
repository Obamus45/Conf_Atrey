#!/usr/bin/env bash
# =============================================================
#  Этап 4. Основные команды: cal, date, ls -a/-l, cd -.
#  Закрывайте каждое окно командой exit для перехода дальше.
# =============================================================
cd "$(dirname "$0")/.."

echo
echo "=== 1. Интерактивно: попробуйте cal, date, ls -la, cd - ==="
python3 -m src.main
echo

echo "=== 2. Все режимы этапа 4 через стартовый скрипт ==="
python3 -m src.main --script scripts/startup_stage4.txt
echo

echo "=== 3. Команды этапа 4 на глубоком VFS ==="
python3 -m src.main --vfs vfs_deep --script scripts/startup_stage4.txt
echo

echo "Все сценарии выполнены."
