import websocket
import pyautogui
import time
import base64
import io
from PIL import Image

def send_screenshot(ws):
    while True:
        screenshot = pyautogui.screenshot()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        ws.send(img_str)
        time.sleep(1)

def on_message(ws, message):
    print("Received message: ", message)

def on_error(ws, error):
    print("WebSocket Error: ", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed: ", close_status_code, close_msg)

def on_open(ws):
    send_screenshot(ws)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:5000",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
