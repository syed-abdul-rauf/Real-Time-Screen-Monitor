import cv2
import numpy as np
import pyautogui
import base64
from socketIO_client import SocketIO, LoggingNamespace

def capture_screen():
    # Capture the screen
    screen = pyautogui.screenshot()
    frame = np.array(screen)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def encode_frame(frame):
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def send_frame_to_server(frame, socketio):
    # Send encoded frame to server
    encoded_frame = encode_frame(frame)
    socketio.emit('update_screen', {'image': encoded_frame})

def main():
    socketio = SocketIO('localhost', 5001, LoggingNamespace)

    while True:
        frame = capture_screen()
        send_frame_to_server(frame, socketio)
        cv2.waitKey(100)  # wait 100 ms to reduce CPU usage

if __name__ == '__main__':
    main()
