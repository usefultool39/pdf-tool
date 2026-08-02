#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON=""
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Startup failed: Python 3.10 or newer was not found."
    echo "Install Python first: https://www.python.org/downloads/"
    exit 1
fi

VENV_DIR="$PWD/.venv"
if [ -f "$VENV_DIR/bin/python" ]; then
    PYTHON_EXE="$VENV_DIR/bin/python"
else
    echo "[0/3] Creating local Python virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    PYTHON_EXE="$VENV_DIR/bin/python"
    $PYTHON_EXE -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null || {
        echo "Startup failed: Python 3.10+ is required."
        exit 1
    }
fi

echo "[1/3] Checking dependencies..."
$PYTHON_EXE -m pip install --disable-pip-version-check -r "$PWD/requirements.txt"

echo "[2/3] Starting PDF Tools..."
echo "[3/3] The browser should open automatically."
echo "If it does not open, copy the http://127.0.0.1:PORT address shown below."
echo ""

$PYTHON_EXE "$PWD/app.py"

echo ""
echo "Press Enter to exit..."
read