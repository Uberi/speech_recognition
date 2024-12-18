lint:
# ignore errors for long lines and multi-statement lines
	@pipx run flake8 --ignore=E501,E701,W503 .

rstcheck:
	@pipx run rstcheck --ignore-directives autofunction README.rst reference/*.rst
