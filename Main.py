import os
import sys
import psutil
import datetime
import getpass
import shutil
import subprocess
import ctypes
import winreg
import time
import cv2
import tensorflow as tf
import urllib.request
import numpy as np
from PIL import Image
from pynput import keyboard
from pynput.mouse import Listener
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openpyxl import Workbook

# Global Constants
LOG_FILE = "system_log.txt"
MOUSE_LOG_FILE = "mouse_log.txt"
KEY_LOG_FILE = "keylog.txt"
DIRECTORY_LOG_FILE = "directory_log.txt"
ACCESS_LOG_FILE = "access.log"
FINGERPRINT_IMAGE_PATH = 'fingerprint.jpg'
IMAGE_RECOGNITION_IMAGE_PATH = 'https://example.com/image.jpg'
EXCEL_FILE = "records.xlsx"

# Global Variables
start_time = None
log_entries = []
mouse_log_entries = []
key_log_entries = []
directory_log_entries = []
access_log_entries = []
wb = Workbook()
ws = wb.active
ws.append(["Timestamp", "Event"])

class DirectoryChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        log_entry = f"[{datetime.datetime.now()}] Directory modified: {event.src_path}"
        directory_log_entries.append(log_entry)

    def on_created(self, event):
        log_entry = f"[{datetime.datetime.now()}] New file or directory created: {event.src_path}"
        directory_log_entries.append(log_entry)

    def on_deleted(self, event):
        log_entry = f"[{datetime.datetime.now()}] File or directory deleted: {event.src_path}"
        directory_log_entries.append(log_entry)

def on_press(key):
    try:
        # Log the key press
        log_entries.append(f"[{get_timestamp()}] Key pressed: {key.char}")
    except AttributeError:
        # Log special keys (e.g., Shift, Enter, etc.)
        log_entries.append(f"[{get_timestamp()}] Special key pressed: {key}")

def on_release(key):
    # Stop the listener if the ESC key is pressed
    if key == keyboard.Key.esc:
        return False

def on_move(x, y):
    log_entry = f"Mouse moved to ({x}, {y})"
    mouse_log_entries.append(log_entry)

def on_click(x, y, button, pressed):
    action = "Clicked" if pressed else "Released"
    log_entry = f"Mouse {action}: {button} at ({x}, {y})"
    mouse_log_entries.append(log_entry)

def on_scroll(x, y, dx, dy):
    log_entry = f"Mouse scrolled at ({x}, {y}) - Scroll delta: ({dx}, {dy})"
    mouse_log_entries.append(log_entry)

def log_start_time():
    global start_time
    start_time = datetime.datetime.now()
    log_entry = f"Start Time: {start_time}"
    log_entries.append(log_entry)

def log_shutdown_time():
    shutdown_time = datetime.datetime.now()
    log_entry = f"Shutdown Time: {shutdown_time}"
    log_entries.append(log_entry)

def check_if_already_running():
    process_name = os.path.basename(__file__).split(".")[0]
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

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

def preprocess_image(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, 0)

    # Apply Gaussian blur to reduce noise
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply adaptive thresholding to enhance fingerprint ridges
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return image

def extract_features(image):
    # Apply morphological operations to remove small gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    # Find and draw contours around the fingerprint region
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (255, 255, 255), thickness=2)

    # Extract the largest contour as the fingerprint region
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Crop the fingerprint region
        fingerprint = image[y:y+h, x:x+w]

        return fingerprint

    return None

def fingerprint_recognition(image_path):
    # Preprocess the fingerprint image
    preprocessed_image = preprocess_image(image_path)

    # Extract fingerprint features
    fingerprint = extract_features(preprocessed_image)

    # Display the preprocessed image and extracted fingerprint
    cv2.imshow("Preprocessed Image", preprocessed_image)
    if fingerprint is not None:
        cv2.imshow("Extracted Fingerprint", fingerprint)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def preprocess_image(image_path):
    # Download the image
    urllib.request.urlretrieve(image_path, 'image.jpg')

    # Load and preprocess the image
    image = Image.open('image.jpg')
    image = image.resize((299, 299))
    image = np.array(image) / 255.0
    image = (image - 0.5) * 2.0
    image = np.expand_dims(image, axis=0)

    return image

def image_recognition(image_path):
    # Preprocess the image
    image = preprocess_image(image_path)

    # Make predictions
    predictions = model.predict(image)
    decoded_predictions = tf.keras.applications.imagenet_utils.decode_predictions(predictions, top=3)[0]

    # Print the top 3 predictions
    for _, label, probability in decoded_predictions:
        print(f'{label}: {probability*100:.2f}%')

def on_move(x, y):
    log_entry = f"Mouse moved to ({x}, {y})"
    write_log(log_entry)

def on_click(x, y, button, pressed):
    action = "Clicked" if pressed else "Released"
    log_entry = f"Mouse {action}: {button} at ({x}, {y})"
    write_log(log_entry)

def on_scroll(x, y, dx, dy):
    log_entry = f"Mouse scrolled at ({x}, {y}) - Scroll delta: ({dx}, {dy})"
    write_log(log_entry)

def write_log(log_entry):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry + "\n")

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

    if is_admin():
        create_task()
    else:
        # Relaunch the script with administrator privileges
        python_executable = get_python_executable()
        script_path = os.path.abspath(__file__)
        subprocess.run(["runas", "/noprofile", "/user:Administrator", f'"{python_executable}" "{script_path}"'])

    # Save the log entries to an Excel sheet
    import pandas as pd

    log_data = pd.read_csv("system_log.txt", sep=":", header=None, names=["Action", "Timestamp"])
    log_data.to_excel("system_log.xlsx", index=False)
