# Utility makefile for CC API

all:
	echo "Pick a better target"

smoke-test:
	pytest -m 'smoke'

quick-test:
	pytest -m 'not slow'

coverage-test:
	pytest --cov=src --cov-report=html

run-api:
	./run-dev-server.sh	

.PHONY: clean-all

clean-all:
	$(RM) test-db.sqlite
	$(RM) dev-db.sqlite
	$(RM) .coverage
	$(RM) -r .pytest_cache
	$(RM) -r htmlcov
