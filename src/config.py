import os
import json
from pathlib import Path

class ConfigManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_dir = Path.home() / ".config" / "melora"
            self.config_file = self.config_dir / "config.json"
            
            # Default configuration
            self.settings = {
                "general": {
                    "language": "auto",
                    "startup": False,
                    "notifications": True
                },
                "installation": {
                    "auto_install_deps": True,
                    "default_method": "system",
                    "silent_mode": False,
                    "use_sudo": True
                },
                "appimage": {
                    "save_path": str(Path.home() / "Applications"),
                    "auto_shortcut": True,
                    "auto_execute_perms": True
                },
                "security": {
                    "check_checksum": True,
                    "warn_untrusted": True,
                    "virustotal_api_key": ""
                },
                "advanced": {
                    "detailed_logs": False,
                    "terminal_backend": "bash",
                    "debug_mode": False
                },
                "updates": {
                    "auto_update": False
                },
                "appearance": {
                    "accent_color": "blue",
                    "deep_dark": False
                }
            }
            self.load()
            self.initialized = True
            
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Update dict keys recursively to preserve defaults for new items
                    for category, values in loaded.items():
                        if category in self.settings and isinstance(values, dict):
                            self.settings[category].update(values)
            except Exception as e:
                print(f"Error loading config: {e}")
                
    def save(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, category, key):
        return self.settings.get(category, {}).get(key)
        
    def set(self, category, key, value):
        if category in self.settings:
            self.settings[category][key] = value
            self.save()
