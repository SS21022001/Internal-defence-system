import psutil
import datetime

def log_start_time():
    start_time = datetime.datetime.now()
    log_entry = f"Start Time: {start_time}"
    with open("system_log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

def log_shutdown_time():
    shutdown_time = datetime.datetime.now()
    log_entry = f"Shutdown Time: {shutdown_time}"
    with open("system_log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

# Register the start time
log_start_time()

# Your main program logic goes here

# Register the shutdown time before exiting the program
log_shutdown_time()
