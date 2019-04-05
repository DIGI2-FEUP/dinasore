#!/usr/bin/env bash

ip_address=localhost
port=61499

# Runs the unitary tests
# python3.6 tests/__init__.py

# Runs the dinasore component
echo "starting dinasore server..."
python3.6 core/main.py -a "$ip_address" -p "$port" &
echo "done."

# Runs the script responsible to upload the fb's configuration to the component
echo "sending the configuration..."
python3.6 resources/upload/upload_client.py -a "$ip_address" -p "$port"
echo "configuration sent."
