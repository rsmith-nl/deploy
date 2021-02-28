.PHONY: help uninstall tests

# Installation locations
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

help::
	@echo "As a normal user, you can:"
	@echo "* 'make check' to check the program with pylama."
	@echo "* 'make tests' to run the test suite."
	@echo "As the root user, you can:"
	@echo "* 'make install' to install the “deploy” script in /usr/local/bin."

check::
	pylama deploy.py

tests::
	py.test -v tests.py

install::
	@test `id -u` -eq 0 || { echo "Only root can install"; exit 1; }
	@install -Cv deploy.py /usr/local/bin/deploy
