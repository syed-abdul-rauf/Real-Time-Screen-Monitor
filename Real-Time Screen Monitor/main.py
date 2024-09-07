from flask import Flask, render_template, request, redirect, Response, jsonify
import pyautogui
import cv2
import numpy as np
from datetime import datetime

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
    
    if username in live_users and live_users[username]['password'] == password:
        return redirect(f'/employee_dashboard/{username}')
    
    return "Invalid credentials"

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', live_users=live_users)

@app.route('/employee_dashboard/<username>')
def employee_dashboard(username):
    user = live_users.get(username)
    if user:
        return render_template('employee_dashboard.html', username=username)
    return "User not found."

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
    password = request.form.get('password')
    live_users[username] = {
        'password': password,
        'connected': True,
        'connect_time': datetime.now()
    }
    return redirect(f'/employee_dashboard/{username}')

@app.route('/disconnect_user', methods=['POST'])
def disconnect_user():
    username = request.form.get('username')
    if username in live_users:
        live_users[username]['connected'] = False
        live_users[username]['disconnect_time'] = datetime.now()
    return redirect(f'/employee_dashboard/{username}')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    live_users[username] = {
        'password': password,
        'connected': False,
        'connect_time': None,
        'disconnect_time': None
    }
    return redirect('/admin_dashboard')

@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if username in live_users:
        del live_users[username]
    return redirect('/admin_dashboard')

if __name__ == "__main__":
    app.run(debug=True)
