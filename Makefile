setup:
	uv sync
	uvx pre-commit install

dev:
	uv run python pyclashbot

lint:
	uvx pre-commit run --all-files

# Offline by default (pytest addopts carries -m "not emulator"); safe everywhere.
test:
	uv run pytest

# Full emulator suite (clash jobs + memu infra), ordered, stop at first failure.
# Needs a live emulator parked on the Clash main menu. EMULATOR defaults to memu.
test-emulator:
	uv run pytest -m emulator -x --emulator $(or $(EMULATOR),memu)

test-all: test test-emulator

build-msi:
	uv run --group build .\scripts\setup_msi.py bdist_msi

build-dmg:
	uv run --group build scripts/setup_macos.py --target-version v0.0.0-local
