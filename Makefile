.PHONY: development hook

development:
	@echo "\nRunning Streamline in development mode..."
	fastapi dev src/main.py

check:
	@echo "\nRunning pre-commit all or a specific hook..."
	pre-commit run $(filter-out $@,$(MAKECMDGOALS))

# Avoid treating the argument as a target
%:
	@: