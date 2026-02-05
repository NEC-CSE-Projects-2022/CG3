#!/bin/bash

# Exit on error
set -e

echo "==> Installing system dependencies"
apt-get update -q
export DEBIAN_FRONTEND=noninteractive
apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
echo "==> Upgrading pip"
python3 -m pip install --upgrade pip

# Install Python dependencies
echo "==> Installing Python dependencies"
pip3 install -r requirements.txt

# Create and activate virtual environment
echo "==> Creating virtual environment"
python3 -m venv /opt/render/venv
source /opt/render/venv/bin/activate

# Upgrade pip
echo "==> Upgrading pip"
pip install --upgrade pip==22.0.0

# Install wheel first
pip install wheel==0.38.0

# Install setuptools explicitly
pip install setuptools==65.5.0

# Now install requirements
echo "==> Installing requirements"
pip install -r requirements.txt

# Install in development mode
pip install -e .

echo "==> Build completed successfully"
