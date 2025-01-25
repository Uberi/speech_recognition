lint:
# ignore errors for long lines and multi-statement lines
	@pipx run flake8 --ignore=E501,E701,W503 --extend-exclude .venv,venv,build --doctests .

rstcheck:
# PyPI does not support Sphinx directives and roles
	@pipx run rstcheck README.rst 
	@pipx run rstcheck[sphinx] --ignore-directives autofunction reference/*.rst

distribute:
	@pipx run build
	@pipx run twine check dist/*

publish:
# Set PYPI_API_TOKEN before `make publish`
	@test -n "${PYPI_API_TOKEN}"
	@pipx run twine upload -u __token__ -p ${PYPI_API_TOKEN} dist/*
