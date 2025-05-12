format:
	black .

lint:
	pylint .

isort:
	isort .

dotenv:
	dotenv-linter .env

security:
	bandit -r src

check: format isort lint dotenv security