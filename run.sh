#!/usr/bin/env bash
# Запуск эмулятора (вариант 26, этап 1).
# Все аргументы передаются в приложение, например: ./run.sh --demo
set -euo pipefail
cd "$(dirname "$0")"
python3 -m src.main "$@"
