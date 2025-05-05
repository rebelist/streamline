.PHONY: development start shutdown check tests coverage

development:
	@echo "\nRunning Streamline in development mode..."
	#colima start --profile streamline --network-address
	docker-compose --profile development up -d
	fastapi dev src/streamline/handlers/api

start:
	@echo "\nRunning Streamline..."
	# colima start --profile streamline --network-address
	docker-compose --profile production up -d

shutdown:
	@echo "\nStopping Streamline..."
	docker-compose --profile development down
	# colima stop --profile streamline

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

# Avoid treating the argument as a target
%:
	@: