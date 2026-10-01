# Сборка и тесты эмулятора (вариант 26).

PYTHON ?= python3

.PHONY: run demo test test-os

run:
	$(PYTHON) -m src.main

demo:
	$(PYTHON) -m src.main --demo

test:
	$(PYTHON) -m pytest -q

test-os:
	bash scripts/test_config.sh
