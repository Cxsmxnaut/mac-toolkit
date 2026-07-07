#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/pkg"
BUILD_CACHE_DIR="${ROOT_DIR}/build/cache"
PAYLOAD_DIR="${BUILD_DIR}/payload"
CLEAN_PAYLOAD_DIR="${BUILD_DIR}/payload-clean"
APP_DIR="${PAYLOAD_DIR}/usr/local/lib/mac-toolkit"
OUTPUT_DIR="${ROOT_DIR}/dist"
PYTHON_BOOTSTRAP_VERSION="${PYTHON_BOOTSTRAP_VERSION:-3.11.9}"
PYTHON_BOOTSTRAP_URL="${PYTHON_BOOTSTRAP_URL:-https://www.python.org/ftp/python/${PYTHON_BOOTSTRAP_VERSION}/python-${PYTHON_BOOTSTRAP_VERSION}-macos11.pkg}"
VERSION="$(python3 - "${ROOT_DIR}/pyproject.toml" <<'PY'
import tomllib
import sys

with open(sys.argv[1], "rb") as handle:
    print(tomllib.load(handle)["project"]["version"])
PY
)"

export COPYFILE_DISABLE=1

command -v pkgbuild >/dev/null 2>&1 || {
  echo "pkgbuild is required and is available on macOS with Command Line Tools." >&2
  exit 1
}

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required." >&2
  exit 1
}

rm -rf "${BUILD_DIR}" "${OUTPUT_DIR}"
mkdir -p "${APP_DIR}" "${OUTPUT_DIR}" "${BUILD_CACHE_DIR}"

rsync -a \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "venv" \
  --exclude "build" \
  --exclude "dist" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude ".DS_Store" \
  --exclude "._*" \
  "${ROOT_DIR}/" "${APP_DIR}/"

python3 -m pip download \
  --dest "${APP_DIR}/wheelhouse" \
  --requirement "${ROOT_DIR}/requirements.txt" \
  "pip" "setuptools>=68" "wheel"

mkdir -p "${APP_DIR}/bootstrap"
python3 - "${PYTHON_BOOTSTRAP_URL}" "${BUILD_CACHE_DIR}/Python-${PYTHON_BOOTSTRAP_VERSION}.pkg" <<'PY'
import sys
import urllib.request
from pathlib import Path

url = sys.argv[1]
dest = Path(sys.argv[2])
if dest.exists() and dest.stat().st_size > 10_000_000:
    print(f"Using cached Python bootstrap package: {dest}")
    raise SystemExit(0)

print(f"Downloading Python bootstrap package: {url}")
partial = dest.with_suffix(".pkg.partial")
last_error = None
for attempt in range(1, 4):
    try:
        with urllib.request.urlopen(url, timeout=60) as response, open(partial, "wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
        partial.replace(dest)
        break
    except Exception as exc:
        last_error = exc
        print(f"Download attempt {attempt} failed: {exc}", file=sys.stderr)
else:
    raise SystemExit(f"Could not download Python bootstrap package: {last_error}")
print(f"Saved {dest}")
PY
cp "${BUILD_CACHE_DIR}/Python-${PYTHON_BOOTSTRAP_VERSION}.pkg" "${APP_DIR}/bootstrap/Python-${PYTHON_BOOTSTRAP_VERSION}.pkg"

find "${PAYLOAD_DIR}" -name "._*" -delete
xattr -cr "${PAYLOAD_DIR}" 2>/dev/null || true
find "${PAYLOAD_DIR}" -exec xattr -d com.apple.provenance {} \; 2>/dev/null || true

python3 - "${PAYLOAD_DIR}" "${CLEAN_PAYLOAD_DIR}" <<'PY'
import os
import shutil
import stat
import sys
from pathlib import Path

source = Path(sys.argv[1])
dest = Path(sys.argv[2])
if dest.exists():
    shutil.rmtree(dest)

for root, dirs, files in os.walk(source):
    root_path = Path(root)
    relative = root_path.relative_to(source)
    target_root = dest / relative
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copymode(root_path, target_root, follow_symlinks=False)

    dirs[:] = [name for name in dirs if not name.startswith("._")]
    for name in files:
        if name.startswith("._") or name == ".DS_Store":
            continue
        source_file = root_path / name
        target_file = target_root / name
        if source_file.is_symlink():
            target_file.symlink_to(os.readlink(source_file))
            continue
        with open(source_file, "rb") as reader, open(target_file, "wb") as writer:
            shutil.copyfileobj(reader, writer)
        mode = stat.S_IMODE(source_file.stat().st_mode)
        target_file.chmod(mode)
PY

mkdir -p "${CLEAN_PAYLOAD_DIR}/Applications/Mac Toolkit.app/Contents/MacOS"
mkdir -p "${CLEAN_PAYLOAD_DIR}/Applications/Mac Toolkit.app/Contents/Resources"
cat > "${CLEAN_PAYLOAD_DIR}/Applications/Mac Toolkit.app/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>Mac Toolkit</string>
  <key>CFBundleIdentifier</key>
  <string>com.mactoolkit.app</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>Mac Toolkit</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>${VERSION}</string>
  <key>CFBundleVersion</key>
  <string>${VERSION}</string>
  <key>LSMinimumSystemVersion</key>
  <string>12.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
</dict>
</plist>
PLIST

cat > "${CLEAN_PAYLOAD_DIR}/Applications/Mac Toolkit.app/Contents/MacOS/Mac Toolkit" <<'SH'
#!/bin/bash
LOG_DIR="${HOME}/Library/Logs/Mac Toolkit"
LOG_FILE="${LOG_DIR}/gui.log"
mkdir -p "${LOG_DIR}"
{
  echo "Launching Mac Toolkit GUI: $(date)"
  exec /usr/local/bin/mactoolkit-gui
} >> "${LOG_FILE}" 2>&1
SH
chmod 0755 "${CLEAN_PAYLOAD_DIR}/Applications/Mac Toolkit.app/Contents/MacOS/Mac Toolkit"

pkgbuild \
  --root "${CLEAN_PAYLOAD_DIR}" \
  --scripts "${ROOT_DIR}/packaging/scripts" \
  --filter '.*\._.*' \
  --filter '.*\.DS_Store' \
  --identifier "com.mactoolkit.cli" \
  --version "${VERSION}" \
  --install-location "/" \
  "${OUTPUT_DIR}/MacToolkit-${VERSION}.pkg"

echo "Built ${OUTPUT_DIR}/MacToolkit-${VERSION}.pkg"
