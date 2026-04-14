#!/bin/bash
# Melora Flatpak Wrapper (Corrected for Flathub)
export PYTHONPATH=$PYTHONPATH:/app/share/melora
exec python3 /app/share/melora/main.py "$@"
