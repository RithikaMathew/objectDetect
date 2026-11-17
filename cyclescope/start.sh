#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_dir"
exec "$repo_dir/cyclescope/.venv/bin/python" "$repo_dir/cyclescope/scripts/dev.py"
