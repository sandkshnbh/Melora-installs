import os
import shutil
import subprocess
import threading
from src.desktop import install_appimage
from src.config import ConfigManager
from src.database import AppDatabase

def is_flatpak():
    return os.path.exists("/.flatpak-info")

def detect_package_manager():
    # If in Flatpak, we must check on host
    if is_flatpak():
        try:
            for pm in ["apt", "dnf", "pacman"]:
                res = subprocess.run(["flatpak-spawn", "--host", "which", pm], capture_output=True)
                if res.return_code == 0:
                    return pm
        except: pass
        return None
    
    if shutil.which("apt"):
        return "apt"
    elif shutil.which("dnf"):
        return "dnf"
    elif shutil.which("pacman"):
        return "pacman"
    return None

def get_package_id(file_path):
    ext = file_path.lower().split(".")[-1]
    if ext == "rpm":
        if not shutil.which("rpm"):
            return os.path.basename(file_path)
        try:
            res = subprocess.run(wrap_cmd(["rpm", "-qp", "--queryformat", "%{NAME}", file_path]), 
                               capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except: return os.path.basename(file_path)
    elif ext == "deb":
        if not shutil.which("dpkg-deb"):
            return os.path.basename(file_path)
        try:
            res = subprocess.run(wrap_cmd(["dpkg-deb", "-f", file_path, "Package"]), 
                               capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except: return os.path.basename(file_path)
    elif ext == "flatpakref":
        # Usually we'd parse the ini, for now use filename or common ID
        return os.path.basename(file_path).replace(".flatpakref", "")
    return os.path.basename(file_path)

def run_installation(file_path: str, log_callback, done_callback):
    def install_thread():
        log_callback(f"Analyzing file: {os.path.basename(file_path)}\n")
        
        if not os.path.exists(file_path):
            log_callback("Error: File does not exist.\n")
            done_callback(False)
            return

        config = ConfigManager()
        cmd = None
        ext = file_path.lower().split(".")[-1]
        
        use_sudo = config.get("installation", "use_sudo")
        sudo_prefix = ["pkexec"] if use_sudo else []

        if ext == "deb":
            pm = detect_package_manager()
            if pm == "apt":
                if config.get("installation", "auto_install_deps"):
                    # Use bash -c to sequence auto-fix and then install
                    full_cmd = f"apt-get --fix-broken install -y && apt-get install -y '{file_path}'"
                    cmd = sudo_prefix + ["bash", "-c", full_cmd]
                else:
                    cmd = sudo_prefix + ["apt-get", "install", "-y", file_path]
            else:
                log_callback("Error: .deb file requires 'apt' but it is not installed.\n")
                done_callback(False)
                return
        elif ext == "rpm":
            pm = detect_package_manager()
            if pm in ["dnf", "yum"]:
                cmd = sudo_prefix + ["dnf", "install", "-y", file_path]
            else:
                log_callback("Error: .rpm file requires 'dnf' but it is not installed.\n")
                done_callback(False)
                return
        elif ext == "flatpakref":
            cmd = ["flatpak", "install", "--user", "-y", "--from", file_path]
        elif ext == "appimage":
            success = install_appimage(file_path, log_callback)
            done_callback(success)
            return
        else:
            log_callback(f"Error: Unsupported file extension .{ext}\n")
            done_callback(False)
            return

        # Execute system package manager
        log_callback(f"Executing: {' '.join(cmd)}\n")
        try:
            # We use Popen to stream the output
            process = subprocess.Popen(wrap_cmd(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                log_callback(line)
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                log_callback("Installation completed successfully!\n")
                
                # Record in database
                db = AppDatabase()
                app_id = get_package_id(file_path)
                db.add_app(os.path.basename(file_path), app_id, ext, file_path)
                
                done_callback(True)
            else:
                log_callback(f"Installation failed with exit code: {return_code}\n")
                done_callback(False)
        except Exception as e:
            log_callback(f"Execution error: {str(e)}\n")
            done_callback(False)

    thread = threading.Thread(target=install_thread, daemon=True)
    thread.start()

def run_uninstallation(app_data, log_callback, done_callback):
    def uninstall_thread():
        app_id = app_data["id"]
        app_type = app_data["type"]
        log_callback(f"Starting uninstallation for: {app_data['name']}\n")
        
        config = ConfigManager()
        use_sudo = config.get("installation", "use_sudo")
        sudo_prefix = ["pkexec"] if use_sudo else []

        cmd = None
        if app_type == "rpm":
            cmd = sudo_prefix + ["dnf", "remove", "-y", app_id]
        elif app_type == "deb":
            cmd = sudo_prefix + ["apt-get", "remove", "-y", app_id]
        elif app_type == "flatpakref":
            # Assuming it was installed per-user
            cmd = ["flatpak", "uninstall", "--user", "-y", app_id]
        elif app_type == "appimage":
            # For AppImage we just delete the file (path is stored in db)
            path = app_data.get("path")
            if path and os.path.exists(path):
                log_callback(f"Removing file: {path}\n")
                try:
                    os.remove(path)
                    
                    # Cleanup desktop shortcut
                    app_stem = Path(path).stem
                    desktop_file = os.path.expanduser(f"~/.local/share/applications/{app_stem}.desktop")
                    if os.path.exists(desktop_file):
                        log_callback(f"Removing shortcut: {desktop_file}\n")
                        os.remove(desktop_file)
                        
                    log_callback("Uninstallation completed successfully!\n")
                    AppDatabase().remove_app(app_id)
                    done_callback(True)
                    return
                except Exception as e:
                    log_callback(f"Error: {e}\n")
                    done_callback(False)
                    return
            else:
                log_callback("Error: AppImage file not found.\n")
                done_callback(False)
                return
        
        if not cmd:
            log_callback("Error: Unknown application type.\n")
            done_callback(False)
            return

        log_callback(f"Executing: {' '.join(cmd)}\n")
        try:
            process = subprocess.Popen(wrap_cmd(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                log_callback(line)
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                log_callback("Uninstallation completed successfully!\n")
                AppDatabase().remove_app(app_id)
                done_callback(True)
            else:
                log_callback(f"Uninstallation failed with code: {return_code}\n")
                done_callback(False)
        except Exception as e:
            log_callback(f"Error: {str(e)}\n")
            done_callback(False)

    thread = threading.Thread(target=uninstall_thread, daemon=True)
    thread.start()
