# Сборка и тесты эмулятора (вариант 26, этап 1).

PYTHON ?= python3

.PHONY: run demo test

run:
	$(PYTHON) -m src.main

demo:
	$(PYTHON) -m src.main --demo

test:
	$(PYTHON) -m pytest -q
