from flask import Flask, render_template, request, redirect, Response
import pyautogui
import cv2
import numpy as np
from datetime import datetime
from xvfbwrapper import Xvfb  # Import Xvfb for virtual display in headless environments

# Start a virtual display (for headless environments like Render)
vdisplay = Xvfb()
vdisplay.start()

app = Flask(__name__)

# Admin credentials
admin_credentials = {
    'username': 'admin',
    'password': 'adminpassword'
}

# Dictionary to store connected users
live_users = {}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check admin credentials
    if username == admin_credentials['username'] and password == admin_credentials['password']:
        return redirect('/admin_dashboard')

    return "Invalid credentials"

@app.route('/admin_dashboard')
def admin_dashboard():
    users = live_users.keys()
    return render_template('admin_dashboard.html', users=users, live_users=live_users)

@app.route('/employee_dashboard/<username>')
def employee_dashboard(username):
    if username in live_users:
        return render_template('employee_dashboard.html', username=username)
    return "User not connected."

# Function to capture and stream the screen
def generate_video_stream():
    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/view_screen/<username>')
def view_screen(username):
    if username in live_users:
        return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "User is not connected."

@app.route('/connect_user', methods=['POST'])
def connect_user():
    username = request.form.get('username')
    live_users[username] = True
    return redirect(f'/employee_dashboard/{username}')

@app.route('/disconnect_user', methods=['POST'])
def disconnect_user():
    username = request.form.get('username')
    live_users.pop(username, None)
    return redirect(f'/employee_dashboard/{username}')

if __name__ == "__main__":
    app.run(debug=True)
