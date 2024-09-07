from flask import Flask, render_template, request, redirect, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    connected = db.Column(db.Boolean, default=False)
    connect_time = db.Column(db.DateTime, nullable=True)
    disconnect_time = db.Column(db.DateTime, nullable=True)

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
    
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return redirect(f'/employee_dashboard/{username}')
    
    return "Invalid credentials"

@app.route('/admin_dashboard')
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users, live_users=live_users)

@app.route('/employee_dashboard/<username>')
def employee_dashboard(username):
    user = User.query.filter_by(username=username).first()
    return render_template('employee_dashboard.html', user=user)

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
    user = User.query.filter_by(username=username).first()
    if user:
        user.connected = True
        user.connect_time = datetime.now()
        live_users[username] = True
        db.session.commit()
    return redirect(f'/employee_dashboard/{username}')

@app.route('/disconnect_user', methods=['POST'])
def disconnect_user():
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        user.connected = False
        user.disconnect_time = datetime.now()
        live_users.pop(username, None)
        db.session.commit()
    return redirect(f'/employee_dashboard/{username}')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    new_user = User(name=name, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect('/admin_dashboard')

if __name__ == "__main__":
    app.run(debug=True)
