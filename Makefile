.PHONY: run-dev run-docker-up run-docker-build run-docker-down run-docker-up-prod run-docker-build-prod run-docker-down-prod run-db-migrate run-db-seed-database run-tests run-linter-checks run-linter-fixes run-hooks-install run-docs-bundle run-get-producer-credentials

run-dev:
	@bash scripts/make/run-dev.sh
	@bash scripts/make/run-docs-bundle.sh

run-docker-up:
	@bash scripts/make/run-docker-up.sh
	@bash scripts/make/run-docs-bundle.sh

run-docker-build:
	@bash scripts/make/run-docker-build.sh
	@bash scripts/make/run-docs-bundle.sh

run-docker-down:
	@bash scripts/make/run-docker-down.sh

run-docker-up-prod:
	@APP_ENV=production bash scripts/make/run-docker-up.sh

run-docker-build-prod:
	@APP_ENV=production bash scripts/make/run-docker-build.sh

run-docker-down-prod:
	@APP_ENV=production bash scripts/make/run-docker-down.sh

run-db-migrate:
	@bash scripts/make/run-db-migrate.sh

run-db-seed-database:
	@bash scripts/make/run-db-seed-database.sh

run-tests:
	@bash scripts/make/run-tests.sh

run-linter-checks:
	@bash scripts/make/run-linter-checks.sh

run-linter-fixes:
	@bash scripts/make/run-linter-fixes.sh

run-hooks-install:
	@bash scripts/make/run-hooks-install.sh

run-docs-bundle:
	@bash scripts/make/run-docs-bundle.sh

run-get-producer-credentials:
	@bash scripts/make/run-get-producer-credentials.sh
