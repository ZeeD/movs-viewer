.PHONY: list
list:
	@grep '^\w*:' Makefile

.PHONY: test
test:
	. ../venv/bin/activate; PYTHONPATH=tests:src python -m unittest discover -s tests

.PHONY: update
update:
	. ../venv/bin/activate; python -mpip install -U -e '.[devtools]'

.PHONY: lint
lint:
	. ../venv/bin/activate; ruff format .; ruff .; mypy .
