setup:
	uv sync
	uvx pre-commit install

dev:
	uv run python pyclashbot

lint:
	uvx pre-commit run --all-files

build-msi:
	uv run --group build .\scripts\setup_msi.py bdist_msi

build-dmg:
	uv run --group build scripts/setup_macos.py --target-version v0.0.0-local
