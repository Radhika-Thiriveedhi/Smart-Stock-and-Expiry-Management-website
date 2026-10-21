# StockWise Automation Makefile

.PHONY: install run build test clean docker-build docker-run

install:
	pip install -r requirements.txt

run:
	python main.py

build:
	python StockWise/build_app_code.py

test:
	python -m unittest discover -s StockWise/tests -p "test_*.py"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t stockwise-app:latest .

docker-run:
	docker run -p 5000:5000 stockwise-app:latest
