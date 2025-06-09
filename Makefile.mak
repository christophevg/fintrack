RUN_CMD=python -m fintrack

apply: env
	$(PYPI_TEMPLATE) verbose apply

update: apply uninstall-env-run install-env-run
