.PHONY: help uninstall tests

# Installation locations
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

help::
	@echo "As a normal user, you can:"
	@echo "'make check' to check the program with pylama."
	@echo "'make tests' to run the test suite."
	@echo "As root, use:"
	@echo "'make install' to install the program."
	@echo "'make uninstall' to remove the program."

check::
	pylama deploy.py


install: deploy.py
	@install -d ${BINDIR}
	install deploy.py ${BINDIR}/deploy

uninstall::
	rm -f ${BINDIR}/deploy

tests::
	py.test -v tests.py
