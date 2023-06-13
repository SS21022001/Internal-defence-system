from pynput.mouse import Listener

LOG_FILE = "mouse_log.txt"

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
    with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
