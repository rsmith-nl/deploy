.PHONY: help uninstall tests

# Installation locations
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

help::
	@echo "As a normal user, you can:"
	@echo "'make check' to check the program with pylama."
	@echo "'make tests' to run the test suite."

check::
	pylama deploy.py

tests::
	py.test -v tests.py
