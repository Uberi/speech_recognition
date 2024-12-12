lint:
# ignore errors for long lines and multi-statement lines
	@pipx run flake8 --ignore=E501,E701,W503 .
