# =============================================================================

# DESCRIPTION:
# Backend logic module for Project Zenith.
# Contains all functions that interact with the operating system to perform
# analysis and cleaning tasks. This module is UI-agnostic.
# =============================================================================

import os
import shutil
import platform
import psutil
import winreg
import ctypes
import time

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def get_system_info():
    """Collects basic system and resource information."""
    try:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage": psutil.cpu_percent(interval=1),
            "ram_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    except Exception as e:
        print(f"Error getting system info: {e}")
        return {}

def find_temp_files():
    """
    Finds common Windows and user temporary files and folders.
    Does not delete anything, only locates and calculates the total size.
    
    Returns:
        dict: A dictionary with 'files_to_clean' (list of paths) and 
              'total_size_mb' (total size in megabytes).
    """
    # Simulate a longer scan to make the threading effect noticeable
    time.sleep(2)
    
    temp_paths = [
        os.environ.get('TEMP'),
        os.path.join(os.environ.get('windir', 'C:\\Windows'), 'Temp')
    ]
    
    files_to_clean = []
    total_size = 0
    
    for path in temp_paths:
        if path and os.path.exists(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        # Only add if it's not a directory link to avoid recursion
                        if os.path.isfile(fp) or os.path.islink(fp):
                            files_to_clean.append(fp)
                            total_size += os.path.getsize(fp)
                    except OSError:
                        # Ignore files that can't be accessed (e.g., in use)
                        continue
                # Also add empty subdirectories for cleanup
                for d in dirnames:
                    dp = os.path.join(dirpath, d)
                    if not os.listdir(dp):
                        files_to_clean.append(dp)

    return {
        "files_to_clean": files_to_clean,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }

def clean_files(file_list):
    """
    Safely deletes a list of files and directories.
    
    Args:
        file_list (list): List of file paths to delete.
    
    Returns:
        int: Number of items that could not be deleted due to errors.
    """
    # Simulate a longer cleaning process
    time.sleep(2)
    
    errors = 0
    for path in file_list:
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            errors += 1
    return errors

def get_startup_programs():
    """
    Gets the list of programs that start with Windows from the Registry.
    
    Returns:
        list: A list of dictionaries, each representing a startup program.
    """
    startup_programs = []
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    startup_programs.append({"name": name, "command": value, "enabled": True})
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        # It's normal for this key to sometimes not exist
        pass
        
    return startup_programs
