import json
import os
import threading
from pathlib import Path

class AppDatabase:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(AppDatabase, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_dir = Path.home() / ".config" / "melora"
            self.db_file = self.db_dir / "installed_apps.json"
            self.lock = threading.Lock()
            self.apps = []
            self.load()
            self.initialized = True
            
    def load(self):
        with self.lock:
            if self.db_file.exists():
                try:
                    with open(self.db_file, 'r', encoding='utf-8') as f:
                        self.apps = json.load(f)
                except Exception as e:
                    print(f"Error loading app database: {e}")
                    self.apps = []
                
    def save(self):
        with self.lock:
            try:
                self.db_dir.mkdir(parents=True, exist_ok=True)
                with open(self.db_file, 'w', encoding='utf-8') as f:
                    json.dump(self.apps, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving app database: {e}")
            
    def add_app(self, name, app_id, app_type, path=None):
        with self.lock:
            # Prevent duplicates
            self.apps = [app for app in self.apps if app['id'] != app_id]
            
            from datetime import datetime
            self.apps.append({
                "name": name,
                "id": app_id,
                "type": app_type,
                "path": path,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        self.save()
        
    def remove_app(self, app_id):
        with self.lock:
            self.apps = [app for app in self.apps if app['id'] != app_id]
        self.save()
        
    def get_all(self):
        return self.apps
