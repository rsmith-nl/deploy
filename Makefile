.PHONY: help uninstall tests

# Installation locations
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

help::
	@echo "As root, use:"
	@echo "'make install' to install the program."
	@echo "'make uninstall' to remove the program."

install: deploy.py
	@install -d ${BINDIR}
	install deploy.py ${BINDIR}/deploy

uninstall::
	rm -f ${BINDIR}/deploy

tests::
	py.test-3.6 -v tests.py

