import os
import threading
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.core.logger import logger
from app.core.reloader import reload_settings


class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, filename: str):
        self.filename = filename
        self._last_reload_time = 0.0

    def on_modified(self, event):
        # Ensure we only react to the specific file
        if event.is_directory:
            return
        
        # Check if the modified file matches our target filename
        # event.src_path is absolute, so we check basename or full match
        if os.path.basename(event.src_path) == self.filename:
            logger.info(f"Detected change in {self.filename}, reloading settings...")
            try:
                reload_settings()
            except Exception as e:
                logger.error(f"Error reloading settings: {e}")


def start_config_watcher(env_file: str = ".env") -> Optional[Observer]:
    """
    Start a background thread to watch the .env file for changes.
    """
    if not os.path.exists(env_file):
        logger.warning(f"Configuration file '{env_file}' not found. Config watcher will not start.")
        return None

    directory = os.path.dirname(os.path.abspath(env_file))
    filename = os.path.basename(env_file)

    handler = ConfigFileHandler(filename)
    observer = Observer()
    observer.schedule(handler, directory, recursive=False)
    
    try:
        observer.start()
        logger.info(f"Config watcher started for: {env_file}")
        return observer
    except Exception as e:
        logger.error(f"Failed to start config watcher: {e}")
        return None
