#!/bin/bash

# Function to install external dependencies on Linux and set up the virtual environment
install_linux() {
    echo "Linux detected..."

    # Updating package list
    echo "Updating package list..."
    sudo apt update

    # Installing ffmpeg
    echo "Installing ffmpeg..."
    sudo apt install -y ffmpeg

    # Installing python3-venv if not already installed
    echo "Checking for python3-venv..."
    sudo apt install -y python3-venv

    # Creating virtual environment in the current project directory
    echo "Creating virtual environment..."
    python3 -m venv venv

    # Activating the virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Installing Python dependencies from requirements.txt
    echo "Installing Python dependencies from requirements.txt..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "requirements.txt not found. Please ensure it exists in the project root."
        exit 1
    fi

    # Installing playwright browsers for scraping
    echo "Installing playwright browsers for scraping..."
    python3 -m playwright install

    # Install host system dependencies for playwright
    echo "Installing host system dependencies for playwright..."
    playwright install-deps

    echo "Setup complete. To activate the virtual environment in the future, run:"
    echo "source venv/bin/activate"
}

# Detect if the script is being run on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    install_linux
else
    echo "This script only supports Linux. Please install dependencies manually."
fi