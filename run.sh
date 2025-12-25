#!/bin/bash

# Configuration
VENV_DIR=".venv"
SCRIPT_NAME="cisdownloader.py"
REQUIREMENTS="requirements.txt"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.8+."
    exit 1
fi

# Create Virtual Environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate Virtual Environment
source "$VENV_DIR/bin/activate"

# Install Dependencies
if [ -f "$REQUIREMENTS" ]; then
    echo "[INFO] Checking/Installing dependencies..."
    pip install -r "$REQUIREMENTS"
else
    echo "[WARNING] $REQUIREMENTS not found. Skipping dependency installation."
fi

# Run the Script
echo
echo "[INFO] Running $SCRIPT_NAME..."
echo
python "$SCRIPT_NAME"

# Deactivate
deactivate
echo
echo "[INFO] Done."
