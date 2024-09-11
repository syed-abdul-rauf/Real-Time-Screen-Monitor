from flask import Flask, render_template, request, redirect, session, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import numpy as np
import os

# Import pyautogui only if we are not in a headless environment
if 'DISPLAY' in os.environ:
    import pyautogui
else:
    pyautogui = None

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this with a secure random value

# Session configurations
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

# SQLAlchemy database setup using PostgreSQL URL
# postgresql://root:tu4nzc3K4FNTH2XWRYj3qQ3bNnjIqzXJ@dpg-cren3f5svqrc73fkr7n0-a.oregon-postgres.render.com/realtime_screenmonitor_db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:tu4nzc3K4FNTH2XWRYj3qQ3bNnjIqzXJ@dpg-cren3f5svqrc73fkr7n0-a.oregon-postgres.render.com:5432/realtime_screenmonitor_db'




app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Database Model for Users
class User(db.Model):
    __tablename__ = 'user3'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_connected = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check hardcoded admin credentials first
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_id'] = -1  # -1 can represent the admin in this simple case
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))

        # Check regular users in the database
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    try:
        # Fetch all users
        users = User.query.all()
        return render_template('admin_dashboard.html', users=users)
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        return render_template('error.html', error="Failed to load admin dashboard")

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

# Function to generate frames for screen capture (only works in non-headless environments)
def generate_video_stream():
    if pyautogui is None:
        print("pyautogui is not available in this environment (likely headless).")
        return b''

    while True:
        screenshot = pyautogui.screenshot()  # Capture screenshot
        frame = np.array(screenshot)  # Convert the screenshot to a numpy array
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV compatibility
        ret, jpeg = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
        if not ret:
            continue
        # Return the frame as a byte stream for display
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/view_screen/<username>')
def view_screen(username):
    if pyautogui is None:
        return "Screen capture is not available in this environment."
    
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error=error), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
