import psutil
import datetime
import os
import getpass
import shutil
import subprocess
import ctypes
import winreg

LOG_FILE = "system_log.txt"

def log_start_time():
    start_time = datetime.datetime.now()
    log_entry = f"Start Time: {start_time}"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry + "\n")

def log_shutdown_time():
    shutdown_time = datetime.datetime.now()
    log_entry = f"Shutdown Time: {shutdown_time}"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry + "\n")

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

if __name__ == "__main__":
    if check_if_already_running():
        print("The program is already running. Exiting...")
    else:
        log_start_time()

        # Your main program logic goes here

        log_shutdown_time()

    if is_admin():
        create_task()
    else:
        # Relaunch the script with administrator privileges
        python_executable = get_python_executable()
        script_path = os.path.abspath(__file__)
        subprocess.run(["runas", "/noprofile", "/user:Administrator", f'"{python_executable}" "{script_path}"'])
