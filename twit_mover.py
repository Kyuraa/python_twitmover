import os
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
DOWNLOADS_FOLDER = str(Path.home() / "Downloads")
TWIT_FOLDER = os.path.join(DOWNLOADS_FOLDER, "twit")
CHECK_INTERVAL = 1  # seconds

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
        
        # Check if file starts with "twit_"
        if filename.startswith("twit_"):
            # Wait to ensure file is completely downloaded
            time.sleep(10)
            
            # Check if file still exists and is accessible
            if not os.path.exists(file_path):
                return
            
            try:
                # Try to open the file to ensure it's not being written to
                with open(file_path, 'rb') as f:
                    pass
                
                # Create twit folder if it doesn't exist
                os.makedirs(TWIT_FOLDER, exist_ok=True)
                
                # Move the file
                destination = os.path.join(TWIT_FOLDER, filename)
                
                # Handle duplicate filenames
                counter = 1
                base_name, extension = os.path.splitext(filename)
                while os.path.exists(destination):
                    new_filename = f"{base_name}_{counter}{extension}"
                    destination = os.path.join(TWIT_FOLDER, new_filename)
                    counter += 1
                
                shutil.move(file_path, destination)
                self.processed_files.add(file_path)
                print(f"✓ Moved: {filename} -> twit/")
                
            except PermissionError:
                print(f"⚠ File still being written: {filename}, will retry...")
            except Exception as e:
                print(f"✗ Error moving {filename}: {e}")

def scan_existing_files():
    """Scan for existing twit_ files in Downloads folder on startup"""
    try:
        for filename in os.listdir(DOWNLOADS_FOLDER):
            if filename.startswith("twit_"):
                file_path = os.path.join(DOWNLOADS_FOLDER, filename)
                if os.path.isfile(file_path):
                    try:
                        os.makedirs(TWIT_FOLDER, exist_ok=True)
                        destination = os.path.join(TWIT_FOLDER, filename)
                        
                        # Handle duplicates
                        counter = 1
                        base_name, extension = os.path.splitext(filename)
                        while os.path.exists(destination):
                            new_filename = f"{base_name}_{counter}{extension}"
                            destination = os.path.join(TWIT_FOLDER, new_filename)
                            counter += 1
                        
                        shutil.move(file_path, destination)
                        print(f"✓ Moved existing: {filename} -> twit/")
                    except Exception as e:
                        print(f"✗ Error moving existing {filename}: {e}")
    except Exception as e:
        print(f"Error scanning existing files: {e}")

def main():
    # Create twit folder if it doesn't exist
    os.makedirs(TWIT_FOLDER, exist_ok=True)
    
    print("=" * 50)
    print("Twitter File Auto-Mover Started")
    print("=" * 50)
    print(f"Monitoring: {DOWNLOADS_FOLDER}")
    print(f"Moving to: {TWIT_FOLDER}")
    print(f"Looking for files starting with: twit_")
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