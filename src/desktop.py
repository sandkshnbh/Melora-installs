import os
import shutil
from pathlib import Path

def install_appimage(src_path: str, log_callback) -> bool:
    try:
        app_name = Path(src_path).stem
        applications_dir = os.path.expanduser("~/Applications")
        os.makedirs(applications_dir, exist_ok=True)
        
        target_path = os.path.join(applications_dir, os.path.basename(src_path))
        
        log_callback(f"Moving AppImage to {target_path}...\n")
        shutil.copy2(src_path, target_path)
        
        log_callback("Setting executable permissions...\n")
        os.chmod(target_path, 0o755)
        
        log_callback("Generating desktop shortcut...\n")
        create_desktop_shortcut(target_path, app_name)
        log_callback(f"AppImage {app_name} installed successfully!\n")
        return True
    except Exception as e:
        log_callback(f"Failed to install AppImage: {e}\n")
        return False

def create_desktop_shortcut(app_path: str, app_name: str):
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    desktop_file = os.path.join(desktop_dir, f"{app_name}.desktop")
    
    # Very basic desktop file, ideally we would extract the icon using --appimage-extract
    content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec="{app_path}"
Icon=application-x-executable
Terminal=false
Categories=Utility;
"""
    with open(desktop_file, "w") as f:
        f.write(content)
        
    os.chmod(desktop_file, 0o755)
