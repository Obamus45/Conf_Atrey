#!/usr/bin/env bash
# =============================================================
#  Этап 5. Дополнительные команды: touch, chmod, vfs-load.
#  Закрывайте каждое окно командой exit для перехода дальше.
# =============================================================
cd "$(dirname "$0")/.."

echo
echo "=== 1. Интерактивно: попробуйте touch, chmod, vfs-load ==="
python3 -m src.main
echo

echo "=== 2. Все режимы этапа 5 через стартовый скрипт ==="
python3 -m src.main --script scripts/startup_stage5.txt
echo

echo "=== 3. Команды этапа 5 на глубоком VFS ==="
python3 -m src.main --vfs vfs_deep --script scripts/startup_stage5.txt
echo

echo "Все сценарии выполнены."
