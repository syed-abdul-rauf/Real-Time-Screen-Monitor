import cv2
import numpy as np
import pyautogui
import base64
from flask_socketio import SocketIO, emit

socketio = SocketIO(message_queue='Your_Redis_URL')

def capture_screen():
    screen = pyautogui.screenshot()
    frame = np.array(screen)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def send_screen():
    while True:
        frame = capture_screen()
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        socketio.emit('screen_frame', {'image': jpg_as_text.decode('utf-8')}, namespace='/screen')

if __name__ == "__main__":
    send_screen()
