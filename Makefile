.PHONY: run-dev run-docker-up run-docker-build run-docker-down run-db-migrate run-db-seed run-tests run-linter-checks run-linter-fixes run-hooks-install

run-dev:
	@bash scripts/make/run-dev.sh

run-docker-up:
	@bash scripts/make/run-docker-up.sh

run-docker-build:
	@bash scripts/make/run-docker-build.sh

run-docker-down:
	@bash scripts/make/run-docker-down.sh

run-db-migrate:
	@bash scripts/make/run-db-migrate.sh

run-db-seed:
	@bash scripts/make/run-db-seed.sh

run-tests:
	@bash scripts/make/run-tests.sh

run-linter-checks:
	@bash scripts/make/run-linter-checks.sh

run-linter-fixes:
	@bash scripts/make/run-linter-fixes.sh

run-hooks-install:
	@bash scripts/make/run-hooks-install.sh
