import socketio
import pyautogui
import numpy as np
import cv2
import base64
import time

# Setup socket client
sio = socketio.Client()
sio.connect('https://real-time-screen-monitor.onrender.com:5000')  # Change to your server's address

def capture_and_send():
    while True:
        # Capture the screen
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode()

        # Send the screen capture
        sio.emit('screen_data', {'image_data': jpg_as_text})
        time.sleep(0.5)  # Adjust the frame rate as needed

@sio.event
def connect():
    print("Connected to the server.")
    capture_and_send()

@sio.event
def disconnect():
    print("Disconnected from the server.")

if __name__ == "__main__":
    capture_and_send()
