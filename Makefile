.PHONY: init dev start shutdown check tests coverage

init:
	@echo "\nInitializing files..."
	@if [ ! -f ".env" ]; then cp ".env.example" ".env"; fi
	@if [ ! -f ".env.prod" ]; then cp ".env.example" ".env.prod"; fi
	@if [ ! -f "settings.ini" ]; then cp "settings.ini.example" "settings.ini"; fi

dev:
	@echo "\nRunning Streamline in development mode..."
	@docker-compose up -d
	fastapi dev src/streamline/handlers/api

start:
	@echo "\nRunning Streamline..."
	@docker-compose --profile prod up -d --remove-orphans
	@docker-compose --profile prod exec -t api uv run streamline database:index
	@sleep 3
	@open http://localhost/dashboards

shutdown:
	@echo "\nStopping Streamline..."
	@docker-compose --profile prod down

check:
	@echo "\nRunning pre-commit all or a specific hook..."
	@pre-commit run $(filter-out $@,$(MAKECMDGOALS))

tests:
	@echo "\nRunning tests..."
	@poetry run pytest -vv  --cache-clear --color=yes --no-header --maxfail=1 --failed-first

coverage:
	@echo "\nGenerating test coverage..."
	@poetry run coverage run -m pytest --no-summary --quiet
	@poetry run coverage html

build:
	@echo "\nBuilding api image..."
	@docker-compose --profile prod build

# Avoid treating the argument as a target
%:
	@: