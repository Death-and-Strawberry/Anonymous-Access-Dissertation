#!/bin/bash
set -e

echo "Setting up Therapy platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies if requested
if [ "$1" = "dev" ]; then
    pip install -r requirements-dev.txt
fi

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration!"
fi

echo "Setup complete!"

# Prompt user to setup Tor
read -p "Do you want to setup Tor hidden service now? (y/n): " setup_tor
if [ "$setup_tor" = "y" or "Y"]; then
    ./scripts/setup_tor.sh
else
    echo "You can setup Tor later with ./scripts/setup_tor.sh"
fi
