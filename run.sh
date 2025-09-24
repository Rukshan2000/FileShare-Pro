#!/bin/bash
# Activate the virtual environment and run the Flask app

# Exit on error
set -e

# Activate venv
source "$(dirname "$0")/venv/bin/activate"

# Run the app
python3 app.py
