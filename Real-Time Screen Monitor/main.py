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

# In-memory storage for users
users = {}
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
    
    # Check user credentials
    user = users.get(username)  # Retrieve the user from the dictionary
    if user and user['password'] == password:
        return redirect(f'/employee_dashboard/{username}')
    
    # If credentials are incorrect, show an error message on the login page
    return render_template('login.html', error="Invalid username or password")

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', users=users, live_users=live_users)

@app.route('/employee_dashboard/<username>')
def employee_dashboard(username):
    user = users.get(username)
    if user:
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
        return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "User is not connected."

@app.route('/connect_user', methods=['POST'])
def connect_user():
    username = request.form.get('username')
    if username in users:
        users[username]['connected'] = True
        users[username]['connect_time'] = datetime.now()
        live_users[username] = True
    return redirect(f'/employee_dashboard/{username}')

@app.route('/disconnect_user', methods=['POST'])
def disconnect_user():
    username = request.form.get('username')
    if username in users:
        users[username]['connected'] = False
        users[username]['disconnect_time'] = datetime.now()
        live_users.pop(username, None)
    return redirect(f'/employee_dashboard/{username}')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Ensure the users dictionary is updated
    if username not in users:
        users[username] = {
            'name': name,
            'username': username,
            'password': password,
            'connected': False,
            'connect_time': None,
            'disconnect_time': None
        }
    return redirect('/admin_dashboard')


if __name__ == "__main__":
    app.run(debug=True)
