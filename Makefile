.PHONY: all lint test

all: lint test

lint:
	pep8 *.py

test:
	python3 -m unittest discover --pattern='*_test.py'
