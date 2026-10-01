#!/usr/bin/env bash
# =============================================================
#  Этап 2. Тест всех параметров командной строки эмулятора.
#  Каждый запуск открывает окно эмулятора: закройте его
#  командой exit, чтобы перейти к следующему сценарию.
# =============================================================
cd "$(dirname "$0")/.."

echo
echo "=== 1. Без параметров (значения по умолчанию) ==="
python3 -m src.main
echo

echo "=== 2. --vfs: нестандартная директория VFS ==="
python3 -m src.main --vfs vfs_sample
echo

echo "=== 3. --script: стартовый скрипт ==="
python3 -m src.main --script scripts/startup_basic.txt
echo

echo "=== 4. Все параметры одновременно ==="
python3 -m src.main --vfs vfs_sample --script scripts/startup_basic.txt
echo

echo "=== 5. --demo: стандартный стартовый скрипт ==="
python3 -m src.main --demo
echo

echo "Все сценарии выполнены."
