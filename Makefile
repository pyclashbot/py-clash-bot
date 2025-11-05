setup:
	uv sync
	uvx pre-commit install

dev:
	uv run python pyclashbot/__main__.py

lint:
	uvx pre-commit run --all-files

build-msi:
	uv run --group build .\scripts\setup_msi.py bdist_msi

web-dev:
	uv run python -m pyclashbot.web_main