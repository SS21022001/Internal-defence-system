from pynput import keyboard

def on_press(key):
    try:
        # Log the key press
        print('Key pressed:', key.char)
    except AttributeError:
        # Log special keys (e.g., Shift, Enter, etc.)
        print('Special key pressed:', key)

def on_release(key):
    # Stop the listener if the ESC key is pressed
    if key == keyboard.Key.esc:
        return False

# Create a listener for key presses
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
