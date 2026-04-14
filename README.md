# Melora Installer

<p align="center">
  <img src="assets/sk.png" width="128" height="128" />
</p>

**Melora** is a sophisticated, open-source Linux application installer designed to provide a seamless and modern installation experience. Built with GTK4 and Libadwaita, it ensures perfect integration with the GNOME desktop environment.

### Key Features:
- **Universal Package Support:** Handles `.deb`, `.rpm`, `.AppImage`, and `.flatpakref` files intelligently.
- **Seamless UI:** A frameless design with bottom navigation and vibrant Cairo-based pulse animations.
- **Internationalization:** Support for 8 languages with automatic system detection and full RTL support for Arabic and Persian.
- **Deep Dark Mode:** A true high-contrast dark theme (#101010) that is easy on the eyes.
- **App Manager:** Built-in manager to view and uninstall applications installed via Melora.

### Installation:
Run directly using Python:
```bash
python3 main.py
```

## Technical Stack
- **Language:** Python 3
- **GUI:** GTK4, Libadwaita
- **Graphics:** Cairo (for custom animations)
- **Packaging:** Flatpak (Ready for Flathub)

## License
This project is licensed under the [MIT License](LICENSE).
