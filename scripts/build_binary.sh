#!/usr/bin/env bash
# Build standalone Hawkeyes binary for Linux (maintainer use).
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Installing PyInstaller..."
python3 -m pip install --quiet pyinstaller

echo "Building hawk binary..."
pyinstaller --onefile --clean --name hawk \
  --hidden-import hawkeyes \
  --hidden-import hawkeyes.cli \
  --hidden-import hawkeyes.scanner \
  --hidden-import hawkeyes.banner \
  --hidden-import hawkeyes.utils.port_parser \
  --hidden-import hawkeyes.utils.services \
  --hidden-import hawkeyes.utils.banner_grabber \
  --hidden-import hawkeyes.utils.formatter \
  hawkeyes/cli.py

ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64)  SUFFIX="x86_64" ;;
    aarch64|arm64) SUFFIX="aarch64" ;;
    *) echo "Unsupported arch: ${ARCH}"; exit 1 ;;
esac

RELEASE_NAME="hawk-linux-${SUFFIX}"
cp dist/hawk "dist/${RELEASE_NAME}"
chmod +x "dist/${RELEASE_NAME}"

echo ""
echo "Built:"
echo "  dist/hawk"
echo "  dist/${RELEASE_NAME}"
echo ""
echo "Upload dist/${RELEASE_NAME} and install.sh to your release host."
echo "See PUBLISHING.md for details."
