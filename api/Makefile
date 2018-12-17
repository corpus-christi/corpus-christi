# Utility makefile for CC API

all:
	echo "Pick a better target"

smoke-test:
	pytest src/test_basics.py

coverage-test:
	pytest --cov=src --cov-report=html

run-api:
	./run-dev-server.sh	

.PHONY: clean-all

clean-all:
	$(RM) test-db.sqlite
	$(RM) dev-db.sqlite
	$(RM) .coverage
	$(RM) .pytest_cache
	$(RM) -r htmlcov
