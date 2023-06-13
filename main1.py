import os
import sys
import getpass
import subprocess
import keyboard
from pynput.mouse import Listener
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
import datetime

LOG_FILE = "system_log.txt"

def log_start_time():
    # Log the start time of the script
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Script started at {timestamp}"
    write_log(log_entry)

def log_shutdown_time():
    # Log the shutdown time of the script
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Script shutdown at {timestamp}"
    write_log(log_entry)

def check_if_already_running():
    # Check if another instance of the script is already running
    script_name = os.path.basename(__file__)
    script_count = sum(1 for proc in subprocess.Popen("tasklist", stdout=subprocess.PIPE, shell=True).stdout.readlines() if script_name.encode() in proc)

    return script_count > 1

def get_python_executable():
    # Get the path to the Python executable
    python_executable = sys.executable
    if not python_executable:
        python_executable = sys.exec_prefix + "\\pythonw.exe"
    return python_executable

def create_task():
    # Create a task in Windows Task Scheduler to run the script on system startup
    python_executable = get_python_executable()
    script_path = os.path.abspath(__file__)
    script_name = os.path.basename(script_path)
    username = getpass.getuser()
    task_name = f"Run {script_name} on Startup"

    # Prepare the command to run the script
    script_command = f'"{python_executable}" "{script_path}"'

    try:
        # Create the task
        subprocess.run(["schtasks", "/create", "/tn", task_name, "/tr", script_command, "/sc", "ONLOGON", "/ru", username, "/f"])
        print(f"Task '{task_name}' created successfully.")
    except subprocess.CalledProcessError:
        print("Failed to create the task.")

def delete_task():
    # Delete the task from Windows Task Scheduler
    script_path = os.path.abspath(__file__)
    script_name = os.path.basename(script_path)
    task_name = f"Run {script_name} on Startup"

    try:
        # Delete the task
        subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"])
        print(f"Task '{task_name}' deleted successfully.")
    except subprocess.CalledProcessError:
        print("Failed to delete the task.")

def is_admin():
    try:
        # Check if the script is running with administrator privileges
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def write_log(log_entry):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry + "\n")

class DirectoryChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"File modified: {event.src_path} - {timestamp}"
        write_log(log_entry)

def on_press(key):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Key pressed: {key} - {timestamp}"
    write_log(log_entry)

def on_release(key):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Key released: {key} - {timestamp}"
    write_log(log_entry)

def preprocess_image(image_path):
    from PIL import Image
    import numpy as np

    # Load and preprocess the image
    image = Image.open(image_path)
    image = image.resize((299, 299))
    image = np.array(image) / 255.0
    image = (image - 0.5) * 2.0
    image = np.expand_dims(image, axis=0)

    return image

def image_recognition(image_path):
    import tensorflow as tf
    from tensorflow.keras.applications import inception_v3
    from tensorflow.keras.applications.imagenet_utils import decode_predictions

    # Load the pre-trained InceptionV3 model
    model = inception_v3.InceptionV3()

    # Preprocess the image
    image = preprocess_image(image_path)

    # Make predictions
    predictions = model.predict(image)
    decoded_predictions = decode_predictions(predictions, top=3)[0]

    # Print the top 3 predictions
    for _, label, probability in decoded_predictions:
        print(f'{label}: {probability * 100:.2f}%')

def on_move(x, y):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Mouse moved to ({x}, {y}) - {timestamp}"
    write_log(log_entry)

def on_click(x, y, button, pressed):
    action = "Clicked" if pressed else "Released"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Mouse {action}: {button} at ({x}, {y}) - {timestamp}"
    write_log(log_entry)

def on_scroll(x, y, dx, dy):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Mouse scrolled at ({x}, {y}) - Scroll delta: ({dx}, {dy}) - {timestamp}"
    write_log(log_entry)

if __name__ == "__main__":
    if check_if_already_running():
        print("The program is already running. Exiting...")
    else:
        log_start_time()

        # Define the directory to monitor
        directory_to_watch = "path/to/directory"

        # Create an observer and handler
        directory_event_handler = DirectoryChangeHandler()
        directory_observer = Observer()
        directory_observer.schedule(directory_event_handler, directory_to_watch, recursive=True)

        # Start the directory observer
        directory_observer.start()

        # Create a listener for key presses
        keypress_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

        # Create a listener for mouse events
        mouse_listener = Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

        # Start the keypress listener
        keypress_listener.start()

        # Start the mouse listener
        mouse_listener.start()

        try:
            # Keep the script running until interrupted
            while True:
                pass
        except KeyboardInterrupt:
            # Stop the directory observer, keypress listener, and mouse listener when interrupted
            directory_observer.stop()
            keypress_listener.stop()
            mouse_listener.stop()

        # Wait for the directory observer, keypress listener, and mouse listener to complete before exiting
        directory_observer.join()
        keypress_listener.join()
        mouse_listener.join()

        log_shutdown_time()

        # Convert the log file to an Excel file
        df = pd.read_csv(LOG_FILE, header=None, names=["Event"])
        excel_file = "system_log.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"System log exported to {excel_file}.")

        # Delete the log file
        os.remove(LOG_FILE)
