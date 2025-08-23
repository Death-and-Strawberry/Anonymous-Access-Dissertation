#!/bin/bash
set -e

echo "Setting up Therapy platform..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m .venv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

#!/usr/bin/env bash
set -e

# Setup ffi-wrapper
echo "Setting up submodule"
cd ffi-bbs-signatures
cargo build --release
cd target/release

# Detect OS and extension
case "$(uname -s)" in
  Darwin)  EXT="dylib" ;;
  Linux)   EXT="so" ;;
  MINGW*|MSYS*|CYGWIN*|Windows_NT) EXT="dll" ;;
  *) echo "Unsupported OS: $(uname -s)" && exit 1 ;;
esac

# Check for the built library
if ls libbbs*."$EXT" 1>/dev/null 2>&1; then
  echo "Found libbbs.$EXT"
else
  echo "❌ libbbs.$EXT not found"
  exit 1
fi

echo "Installing into Python from $BASE_DIR/ffi-bbs-signatures/target/release"
python3 -m pip install "$BASE_DIR/ffi-bbs-signatures/target/release"

cd ../../..


read -p "Do you want to run the program now? (y/n): run" 
if [ "$run" = "y" or "Y"]; then
    ./scripts/run.sh
else
    echo "You can run the ZKP software later with ./scripts/run.sh"
fi