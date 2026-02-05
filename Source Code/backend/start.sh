#!/bin/bash

# Exit on error
set -e

echo "==> Installing Python dependencies"
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo "==> Starting Flask development server"
python app.py
