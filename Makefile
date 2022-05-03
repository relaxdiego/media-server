#
# Run `make help` for help
#
# NOTE: Comments starting with double hashes (##) will appear in the
#       help that gets displayed by `make help`

##
## Available Goals:
##

##   setup        : Sets up all dependencies
.PHONY: setup
setup: .venv/initialized
.venv/initialized:
	@scripts/setup-python
	@touch .venv/initialized

##   deploy       : Deploy the media server config
.PHONY: deploy
deploy:
	scripts/deploy
	pytest

##   clean        : Remove production and development dependencies
.PHONY: clean
clean:
	rm -rf \
	.coverage \
	.pytest_cache \
	.venv \
	coverage.xml \
	htmlcov \
	junit.xml \
	node_modules \
	src/*.egg-info \
	test-results

##   pre-commit   : Run all pre-commit hooks
.PHONY : pre-commit
pre-commit: pre-commit-install
	.venv/bin/pre-commit run --all-files
pre-commit-install: setup .pre-commit-config.yaml
	.venv/bin/pre-commit install

##   requirements : Re-compile requirements.txt from requirements.in
.PHONY : requirements
requirements: requirements.txt
requirements.txt: setup requirements.in scripts/setup-python
	.venv/bin/pip-compile

# From: https://swcarpentry.github.io/make-novice/08-self-doc/index.html
##   help         : Print this help message
.DEFAULT_GOAL := help
.PHONY : help
help : Makefile
	@sed -n 's/^##//p' $<

##
## See README.md for more details.
##
