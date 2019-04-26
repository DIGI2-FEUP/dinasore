#!/usr/bin/env bash

# GENERAL CODE

ip_address=localhost
port=61499

# Runs the unitary tests
# python3.6 tests/__init__.py

# Runs the dinasore component
# echo "starting dinasore server..."
python3.6 core/main.py -a "$ip_address" -p "$port" &
# echo "done."

# CODE FOR MOXA

# Gives permission to use port /dev/ttyS0
sudo chmod 777 /dev/ttyS0

# Sets the default interface (/dev/ttyS0) to RS485-2WIRE
sudo setinterface /dev/ttyS0 1

# Runs the script responsible to upload the fb's configuration to the component
# echo "sending the configuration..."
python3.6 resources/upload/upload_client.py -a "$ip_address" -p "$port"
# echo "configuration sent."
