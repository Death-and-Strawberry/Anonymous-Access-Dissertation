#!/bin/bash
set -e

echo "Setting up Tor hidden service for Therapy platform..."

TOR_DIR="$HOME/.tor"
HIDDEN_SERVICE_DIR="$TOR_DIR/therapy_hidden_service"
TORRC="$TOR_DIR/torrc"

# Create directories
mkdir -p "$HIDDEN_SERVICE_DIR"

# Set proper permissions on Unix
if [ "$(uname)" != "Darwin" ] && [ "$(uname)" != "Linux" ]; then
    echo "Warning: Cannot set permissions on this OS."
else
    chmod 700 "$HIDDEN_SERVICE_DIR" #Tor requires strict access control to operate
fi

# Create torrc if missing
if [ ! -f "$TORRC" ]; then
    echo "Creating user-level torrc at $TORRC..." #Because you would need permissions for non user level files.
    cat <<EOL > "$TORRC"
SocksPort 9050
HiddenServiceDir $HIDDEN_SERVICE_DIR
HiddenServicePort 5000 127.0.0.1:5000
EOL
else
    echo "torrc already exists at $TORRC, skipping creation."
fi

# Start Tor
echo "Starting Tor..."
tor -f "$TORRC" &
TOR_PID=$!

# Wait for .onion hostname
echo "Waiting for Tor to generate your .onion address..."
for i in {1..60}; do
    if [ -f "$HIDDEN_SERVICE_DIR/hostname" ]; then
        echo "Your Therapy platform .onion address is:"
        cat "$HIDDEN_SERVICE_DIR/hostname"
        break
    fi
    sleep 1
done

# Timeout warning
if [ ! -f "$HIDDEN_SERVICE_DIR/hostname" ]; then
    echo "Error: hostname file not found after 60 seconds. Check Tor logs."
fi
