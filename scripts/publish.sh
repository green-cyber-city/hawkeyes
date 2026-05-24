#!/usr/bin/env bash
# Maintainer script — build and upload Hawkeyes to PyPI.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Building Hawkeyes..."
python3 -m pip install --quiet build twine
python3 -m build

echo ""
echo "Built:"
ls -1 dist/

echo ""
echo "Upload with:"
echo "  TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-YOUR_TOKEN python3 -m twine upload dist/*"
echo ""
read -r -p "Upload to PyPI now? [y/N] " confirm
if [[ "${confirm}" =~ ^[Yy]$ ]]; then
  python3 -m twine upload dist/*
  echo ""
  echo "Done. Users can now run: pip install hawkeyes"
fi
