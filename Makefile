PYTHON ?= python3
HELPER = so-where/references/where.py

.PHONY: demo map build check test install
demo:
	$(PYTHON) $(HELPER) --root demo serve --port 8765

map:
	$(PYTHON) $(HELPER) --root maps/local serve --port 8767

build:
	$(PYTHON) $(HELPER) --root demo build
	$(PYTHON) $(HELPER) --root maps/local build

check:
	$(PYTHON) $(HELPER) --root demo check
	$(PYTHON) $(HELPER) --root maps/local check

test:
	$(PYTHON) -m unittest discover -s tests -v

install:
	$(PYTHON) scripts/install_skill.py
