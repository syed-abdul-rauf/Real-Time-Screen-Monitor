from flask import Flask, render_template, request, redirect, session, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import numpy as np
import os
import urllib.parse
import pyautogui

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this with a secure random value

# Session configurations
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# Database credentials
username = 'postgres'
password = 'M@had100'
encoded_password = urllib.parse.quote(password)  # URL encode the password

# Database server details
hostname = 'dpg-cren3f5svqrc73fkr7n0-a.oregon-postgres.render.com'
port = 5432
database_name = 'realtime_screenmonitor_db'

# Construct the SQLALCHEMY_DATABASE_URI with SSL mode required
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{encoded_password}@{hostname}:{port}/{database_name}?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'


# Database Model for Users
class User(db.Model):
    __tablename__ = 'user3'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_connected = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_id'] = -1
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('employee_dashboard'))
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/employee_dashboard')
def employee_dashboard():
    if not session.get('username'):
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    return render_template('employee_dashboard.html', user=user)

@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    name = request.form['name']
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    new_user = User(name=name, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/view_screen/<username>')
def view_screen(username):
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_video_stream():
    if pyautogui is None:
        return b''
    while True:
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error=error), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
