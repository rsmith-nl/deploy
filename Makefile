.PHONY: help uninstall test

# Installation locations
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

help::
	@echo "As root, use:"
	@echo "'make install' to install the program."
	@echo "'make uninstall' to remove the program."

install: deploy.py
	@mkdir -p ${BINDIR}
	cp -p deploy.py ${BINDIR}/deploy
	chmod 755 ${BINDIR}/deploy

uninstall::
	rm -f ${BINDIR}/deploy

test::
	nosetests-3.4 -v tests.py
