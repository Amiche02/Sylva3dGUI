#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

sudo apt-get install libxcb-cursor0
sudo apt-get install python3-tk
sudo apt-get install tcl-dev tk-dev

# Check if python3-venv is installed, and install it if not
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "python3-venv is not installed. Installing..."
    sudo apt-get update -qq
    sudo apt-get install -y python3-venv
else
    echo "python3-venv is already installed."
fi

# Create the ~/Pyvenv directory if it doesn't exist
if [ ! -d "$HOME/Pyvenv" ]; then
    echo "Creating directory ~/Pyvenv..."
    mkdir -p "$HOME/Pyvenv"
else
    echo "~/Pyvenv directory already exists."
fi 

# Create the virtual environment sylva3d
if [ ! -d "$HOME/Pyvenv/sylva3d" ]; then
    echo "Creating virtual environment sylva3d..."
    python3 -m venv "$HOME/Pyvenv/sylva3d"
else
    echo "Virtual environment sylva3d already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment sylva3d..."
source "$HOME/Pyvenv/sylva3d/bin/activate"

# Install requirements from requirements.txt if it exists
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "requirements.txt not found in $SCRIPT_DIR."
fi

# Add CUDA paths to the activate script
ACTIVATE_SCRIPT="$HOME/Pyvenv/sylva3d/bin/activate"
if ! grep -q 'export PATH=/usr/local/cuda-11.8/bin${PATH:+:${PATH}}' "$ACTIVATE_SCRIPT"; then
    echo "Adding CUDA paths to the activate script..."
    echo -e '\n# Add CUDA paths\nexport PATH=/usr/local/cuda-11.8/bin${PATH:+:${PATH}}\nexport LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> "$ACTIVATE_SCRIPT"
else
    echo "CUDA paths are already present in the activate script."
fi

# Confirmation message
echo "Virtual environment sylva3d is now active and dependencies are installed. To deactivate, use the command 'deactivate'."
