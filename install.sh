#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON:-python3}"

if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo "python3 was not found. Install Python 3.11 or newer first." >&2
  exit 1
fi

"$python_bin" - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Mac Toolkit requires Python 3.11 or newer.")
PY

"$python_bin" -m pip install --upgrade pip
"$python_bin" -m pip install .

echo
echo "Installed Mac Toolkit."
echo "Run: mactoolkit"
echo "Or:  mactoolkit run --no-progress"
