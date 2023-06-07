from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime

class DirectoryChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        log_entry = f"[{datetime.datetime.now()}] Directory modified: {event.src_path}"
        with open("directory_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")

    def on_created(self, event):
        log_entry = f"[{datetime.datetime.now()}] New file or directory created: {event.src_path}"
        with open("directory_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")

    def on_deleted(self, event):
        log_entry = f"[{datetime.datetime.now()}] File or directory deleted: {event.src_path}"
        with open("directory_log.txt", "a") as log_file:
            log_file.write(log_entry + "\n")

if __name__ == "__main__":
    # Define the directory to monitor
    directory_to_watch = "path/to/directory"

    # Create an observer and handler
    event_handler = DirectoryChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=True)

    # Start the observer
    observer.start()

    try:
        # Keep the script running until interrupted
        while True:
            pass
    except KeyboardInterrupt:
        # Stop the observer when interrupted
        observer.stop()

    # Wait for the observer to complete before exiting
    observer.join()
