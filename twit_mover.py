import os
import re
import time
import shutil
import ctypes
from ctypes import wintypes
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
DOWNLOADS_FOLDER = str(Path.home() / "Downloads")
TWIT_FOLDER = os.path.join(DOWNLOADS_FOLDER, "twit")
PIXIV_FOLDER = os.path.join(DOWNLOADS_FOLDER, "pixiv")
PIXIV_PATTERN = re.compile(r'^\d+_p\d+')
CHECK_INTERVAL = 1  # seconds


def set_file_timestamps(file_path):
    """Set all file timestamps (creation, modification, access) to current time."""
    now = time.time()

    # Set modification and access times using os.utime
    os.utime(file_path, (now, now))

    # Set creation time on Windows using Windows API
    # Convert Unix timestamp to Windows FILETIME
    EPOCH_DIFF = 116444736000000000  # Difference between 1601 and 1970 in 100ns intervals
    timestamp = int((now * 10000000) + EPOCH_DIFF)

    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)

    # Open file handle
    handle = ctypes.windll.kernel32.CreateFileW(
        file_path,
        256,  # FILE_WRITE_ATTRIBUTES
        0,
        None,
        3,  # OPEN_EXISTING
        128,  # FILE_ATTRIBUTE_NORMAL
        None
    )

    if handle != -1:
        # Set the creation time
        ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(ctime), None, None)
        ctypes.windll.kernel32.CloseHandle(handle)


def get_destination_folder(filename):
    """Determine destination folder based on filename pattern."""
    if filename.startswith("twit_"):
        return TWIT_FOLDER
    elif PIXIV_PATTERN.match(filename):
        return PIXIV_FOLDER
    return None


class TwitFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed_files = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        self.process_file(event.src_path)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        self.process_file(event.src_path)
    
    def process_file(self, file_path):
        if file_path in self.processed_files:
            return

        filename = os.path.basename(file_path)
        dest_folder = get_destination_folder(filename)

        if dest_folder is None:
            return

        # Wait to ensure file is completely downloaded
        time.sleep(10)

        # Check if file still exists and is accessible
        if not os.path.exists(file_path):
            return

        try:
            # Try to open the file to ensure it's not being written to
            with open(file_path, 'rb'):
                pass

            # Create destination folder if it doesn't exist
            os.makedirs(dest_folder, exist_ok=True)

            # Move the file
            destination = os.path.join(dest_folder, filename)

            # Handle duplicate filenames
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(destination):
                new_filename = f"{base_name}_{counter}{extension}"
                destination = os.path.join(dest_folder, new_filename)
                counter += 1

            shutil.move(file_path, destination)
            set_file_timestamps(destination)
            self.processed_files.add(file_path)
            folder_name = os.path.basename(dest_folder)
            print(f"✓ Moved: {filename} -> {folder_name}/")

        except PermissionError:
            print(f"⚠ File still being written: {filename}, will retry...")
        except Exception as e:
            print(f"✗ Error moving {filename}: {e}")

def scan_existing_files():
    """Scan for existing matching files in Downloads folder on startup"""
    try:
        for filename in os.listdir(DOWNLOADS_FOLDER):
            dest_folder = get_destination_folder(filename)
            if dest_folder is not None:
                file_path = os.path.join(DOWNLOADS_FOLDER, filename)
                if os.path.isfile(file_path):
                    try:
                        os.makedirs(dest_folder, exist_ok=True)
                        destination = os.path.join(dest_folder, filename)

                        # Handle duplicates
                        counter = 1
                        base_name, extension = os.path.splitext(filename)
                        while os.path.exists(destination):
                            new_filename = f"{base_name}_{counter}{extension}"
                            destination = os.path.join(dest_folder, new_filename)
                            counter += 1

                        shutil.move(file_path, destination)
                        set_file_timestamps(destination)
                        folder_name = os.path.basename(dest_folder)
                        print(f"✓ Moved existing: {filename} -> {folder_name}/")
                    except Exception as e:
                        print(f"✗ Error moving existing {filename}: {e}")
    except Exception as e:
        print(f"Error scanning existing files: {e}")

def main():
    # Create destination folders if they don't exist
    os.makedirs(TWIT_FOLDER, exist_ok=True)
    os.makedirs(PIXIV_FOLDER, exist_ok=True)

    print("=" * 50)
    print("File Auto-Mover Started")
    print("=" * 50)
    print(f"Monitoring: {DOWNLOADS_FOLDER}")
    print(f"Patterns:")
    print(f"  twit_* -> {TWIT_FOLDER}")
    print(f"  [id]_p[n] -> {PIXIV_FOLDER}")
    print("=" * 50)
    
    # Scan for existing files first
    print("\nScanning for existing files...")
    scan_existing_files()
    print("\nWatching for new files...")
    
    # Set up file system observer
    event_handler = TwitFileHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_FOLDER, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()