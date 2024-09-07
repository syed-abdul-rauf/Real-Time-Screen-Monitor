from flask import Flask, render_template, request, redirect, Response, flash
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages

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

    # Check if user exists
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    
    if user:
        return redirect(f'/employee_dashboard/{username}')
    else:
        # Pass an error message back to the login page
        return render_template('login.html', message="Invalid username or password. Please try again.")


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html', users=users, live_users=live_users)

@app.route('/employee_dashboard/<username>')
def employee_dashboard(username):
    user = users.get(username)
    return render_template('employee_dashboard.html', user=user)

# Dummy function to simulate generating video stream
def generate_video_stream():
    while True:
        # Simulate sending video stream
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
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
    user = users.get(username)
    if user:
        user['connected'] = True
        user['connect_time'] = datetime.now()
        live_users[username] = True
    return redirect(f'/employee_dashboard/{username}')

@app.route('/disconnect_user', methods=['POST'])
def disconnect_user():
    username = request.form.get('username')
    user = users.get(username)
    if user:
        user['connected'] = False
        user['disconnect_time'] = datetime.now()
        live_users.pop(username, None)
    return redirect(f'/employee_dashboard/{username}')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    
    users[username] = {
        'name': name,
        'username': username,
        'password': password,
        'connected': False,
        'connect_time': None,
        'disconnect_time': None
    }
    
    return redirect('/admin_dashboard')

@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if username in users:
        del users[username]
    return redirect('/admin_dashboard')

if __name__ == "__main__":
    app.run(debug=True)
