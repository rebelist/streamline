.PHONY: development start shutdown check tests coverage

development:
	@echo "\nRunning Streamline in development mode..."
	docker-compose up -d
	fastapi dev src/streamline/handlers/api

start:
	@echo "\nRunning Streamline..."
	docker-compose --profile production up -d

shutdown:
	@echo "\nStopping Streamline..."
	docker-compose --profile production down

check:
	@echo "\nRunning pre-commit all or a specific hook..."
	@pre-commit run $(filter-out $@,$(MAKECMDGOALS))

tests:
	@echo "\nRunning tests..."
	@poetry run pytest -vv --color=yes --no-header --maxfail=1 --failed-first

coverage:
	@echo "\nGenerating test coverage..."
	@poetry run coverage run -m pytest --no-summary --quiet
	@poetry run coverage html -d coverage

build:
	@echo "\nBuilding api image..."
	docker-compose --profile production build

# Avoid treating the argument as a target
%:
	@: