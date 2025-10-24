# Makefile for Crowd Management System

# Variables
PYTHON = python
PIP = pip
FLASK = flask

# Default target
.PHONY: help
help:
	@echo "Crowd Management System - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  verify      - Verify installation"
	@echo "  clean       - Clean Python cache files"
	@echo "  docs        - Generate documentation"
	@echo "  docker      - Build Docker image"
	@echo "  help        - Show this help message"

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run the application
.PHONY: run
run:
	$(PYTHON) app.py

# Run tests
.PHONY: test
test:
	$(PYTHON) -m unittest discover tests

# Verify installation
.PHONY: verify
verify:
	$(PYTHON) verify_installation.py

# Clean Python cache files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/

# Generate documentation
.PHONY: docs
docs:
	@echo "Documentation is available in the docs/ directory"

# Build Docker image
.PHONY: docker
docker:
	docker build -t crowd-management-system .

# Run in Docker
.PHONY: docker-run
docker-run:
	docker run -p 5000:5000 crowd-management-system