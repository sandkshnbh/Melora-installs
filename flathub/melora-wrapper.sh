#!/bin/bash
# Melora Flatpak Wrapper
# This script launches the Melora application within the Flatpak environment.
# The engine handles host-spawning automatically for installation commands.

export PYTHONPATH=$PYTHONPATH:/app/share/melora
exec python3 /app/share/melora/main.py "$@"
