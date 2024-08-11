#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Install necessary system packages
sudo apt-get install -y libxcb-cursor0 python3-tk

# Check if conda is installed
if ! command -v conda >/dev/null 2>&1; then
    echo "Conda is not installed. Please install conda and try again."
    exit 1
fi

# Create the conda environment sylva3d if it doesn't exist
if ! conda info --envs | grep -q "^sylva3d "; then
    echo "Creating conda environment sylva3d..."
    conda create --name sylva3d -y python=3.10
else
    echo "Conda environment sylva3d already exists."
fi

# Activate the conda environment
echo "Activating conda environment sylva3d..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate sylva3d || exit 1

# Install requirements from requirements.txt if it exists
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "requirements.txt not found in $SCRIPT_DIR."
fi

# Confirmation message
echo "Conda environment sylva3d is now active and dependencies are installed. To deactivate, use the command 'conda deactivate'."
