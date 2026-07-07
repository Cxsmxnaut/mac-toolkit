#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON:-python3}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
install_dir="${HOME}/Library/Application Support/Mac Toolkit"
venv_dir="${install_dir}/.venv"
bin_dir="${HOME}/.local/bin"

if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo "python3 was not found. Install Python 3.11 or newer first." >&2
  exit 1
fi

"$python_bin" - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Mac Toolkit requires Python 3.11 or newer.")
PY

mkdir -p "${install_dir}" "${bin_dir}"
"$python_bin" -m venv "${venv_dir}"
"${venv_dir}/bin/python" -m pip install --upgrade pip
"${venv_dir}/bin/python" -m pip install "${script_dir}"

cat > "${bin_dir}/mactoolkit" <<SH
#!/usr/bin/env bash
exec "${venv_dir}/bin/mactoolkit" "\$@"
SH
chmod 0755 "${bin_dir}/mactoolkit"

echo
echo "Installed Mac Toolkit."
echo "Run: ${bin_dir}/mactoolkit"
echo "Or add ${bin_dir} to PATH and run: mactoolkit run --no-progress"
