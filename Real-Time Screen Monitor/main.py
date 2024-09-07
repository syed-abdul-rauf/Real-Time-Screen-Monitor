from flask import Flask, render_template, request, redirect, Response, jsonify
import pyautogui
import cv2
import numpy as np
from datetime import datetime
import os
import json

app = Flask(__name__)

# Admin credentials
admin_credentials = {
    'username': 'admin',
    'password': 'adminpassword'
}

# In-memory storage for users
users = []
live_users = {}

# Load users from a file if it exists
def load_users():
    global users
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            users = json.load(file)

# Save users to a file
def save_users():
    with open('users.json', 'w') as file:
        json.dump(users, file)

# Load users at the start of the application
load_users()

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

    # Check user credentials
    for user in users:
        if user['username'] == username and user['password'] == password:
            return redirect(f'/employee_dashboard/{username}')
    
    # If credentials are incorrect, show an error message on the login page
    return render_template('login.html', error="Invalid username or password")

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', users=users, live_users=live_users)

@app.route('/employee_dashboard/<username>')
def employee_dashboard(username):
    for user in users:
        if user['username'] == username:
            return render_template('employee_dashboard.html', user=user)
    return "User not found", 404

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
        # Live stream the user's screen
        return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "User is not connected."

@app.route('/connect_user', methods=['POST'])
def connect_user():
    username = request.form.get('username')
    for user in users:
        if user['username'] == username:
            user['connected'] = True
            user['connect_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            live_users[username] = user
            save_users()
    return redirect(f'/employee_dashboard/{username}')

@app.route('/disconnect_user', methods=['POST'])
def disconnect_user():
    username = request.form.get('username')
    if username in live_users:
        live_users.pop(username, None)
    for user in users:
        if user['username'] == username:
            user['connected'] = False
            user['disconnect_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_users()
    return redirect(f'/employee_dashboard/{username}')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')

    # Add user to the users list
    new_user = {
        'name': name,
        'username': username,
        'password': password,
        'connected': False,
        'connect_time': None,
        'disconnect_time': None
    }

    # Ensure that we are not adding duplicate users
    if not any(user['username'] == username for user in users):
        users.append(new_user)
        save_users()
    return redirect('/admin_dashboard')

if __name__ == "__main__":
    app.run(debug=True)
