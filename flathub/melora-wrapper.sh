#!/bin/bash
# Melora Flatpak Wrapper (Standardized Structure)
# The code is located in /app/lib/melora

export PYTHONPATH=$PYTHONPATH:/app/lib/melora
exec python3 /app/lib/melora/main.py "$@"
