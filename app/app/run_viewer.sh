#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Build the path to the main.py script
MAIN_SCRIPT="${SCRIPT_DIR}/3d_viewer/main.py"

# Run the Python script
python3 "$MAIN_SCRIPT"
