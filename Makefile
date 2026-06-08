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

# Full live-emulator suite, ordered, stop at first failure. --integration flips the
# default marker and selects a backend; the first SUITE tests boot the emulator and
# launch Clash. Backend resolves from EMULATOR / a cached pick / interactive menu;
# ADB_SERIAL is optional and sticky.
test-emulator:
	uv run pytest -x -s --integration $(if $(EMULATOR),--emulator $(EMULATOR)) $(if $(ADB_SERIAL),--adb-serial $(ADB_SERIAL))

test-all: test test-emulator

build-msi:
	uv run --group build .\scripts\setup_msi.py bdist_msi

build-dmg:
	uv run --group build scripts/setup_macos.py --target-version v0.0.0-local
