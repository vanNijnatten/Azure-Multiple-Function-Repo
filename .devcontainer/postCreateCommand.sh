#!/usr/bin/env bash
set -euo pipefail

uv sync
uv run scripts/init_local_settings.py
uv run pre-commit install
