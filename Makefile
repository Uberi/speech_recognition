lint:
# ignore errors for long lines and multi-statement lines
	@pipx run flake8 --ignore=E501,E701,W503 .

rstcheck:
# PyPI does not support Sphinx directives and roles
	@pipx run rstcheck README.rst 
	@pipx run rstcheck[sphinx] --ignore-directives autofunction reference/*.rst

distribute:
	@pipx run build
	@pipx run twine check dist/*
