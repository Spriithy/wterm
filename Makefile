SHELL = /bin/bash

#-------------------------------------------------------------------------------

.PHONY: build
build:
	@echo "Building..."
	python3 setup.py bdist_wheel

#-------------------------------------------------------------------------------

.PHONY: install
install:
	@echo "Installing..."
	pip install -U wterm

#-------------------------------------------------------------------------------

.PHONY: uninstall
uninstall:
	@echo "Uninstalling..."
	pip uninstall -y wterm

#-------------------------------------------------------------------------------

.PHONY: update
update: uninstall install

#-------------------------------------------------------------------------------

.PHONY: clean
clean:
	@echo "Cleaning..."
	rm -rf build dist *.egg-info __pycache__
