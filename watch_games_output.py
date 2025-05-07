import time
import os
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil  # pip install psutil

WATCH_DIR = "./games_output"
ROJO_PROJECT = "default.project.json"  # Change to your actual Rojo project file

def is_rojo_serve_running():
    """Check if 'rojo serve' is already running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'rojo' in proc.info['name'] and 'serve' in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def start_rojo_serve():
    """Start 'rojo serve' in the background if not already running."""
    if not is_rojo_serve_running():
        print("Starting Rojo serve...")
        # Start as a background process
        subprocess.Popen(
            ["rojo", "serve", ROJO_PROJECT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)  # Give Rojo a moment to start
    else:
        print("Rojo serve is already running.")

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".lua"):
            print(f"New Lua script detected: {event.src_path}")
            print("If Rojo serve is running, Roblox Studio will hot-reload the script automatically.")
            import shutil
            filename = os.path.basename(event.src_path)
            # Routing logic based on filename suffix
            if filename.endswith('_server.lua'):
                target_dir = os.path.join("src", "server")
            elif filename.endswith('_shared.lua'):
                target_dir = os.path.join("src", "shared")
            elif filename.endswith('_client.lua'):
                target_dir = os.path.join("src", "client")
            else:
                target_dir = os.path.join("src", "server")  # Default
            os.makedirs(target_dir, exist_ok=True)
            dest_path = os.path.join(target_dir, filename)
            try:
                shutil.copy(event.src_path, dest_path)
                print(f"Copied {event.src_path} to {dest_path}")
            except Exception as e:
                print(f"Error copying file: {e}")
            # TODO: Add logic for src/shared and src/client as needed

if __name__ == "__main__":
    os.makedirs(WATCH_DIR, exist_ok=True)
    start_rojo_serve()
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    print(f"Watching {WATCH_DIR} for new Lua scripts...")
    print("Make sure Roblox Studio is open with the Rojo plugin enabled and your project loaded.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



