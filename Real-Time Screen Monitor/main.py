from flask import Flask, render_template, request, redirect, session, url_for, Response
import cv2
import numpy as np
import os
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

# Import pyautogui only if we are not in a headless environment
if 'DISPLAY' in os.environ:
    import pyautogui
else:
    pyautogui = None

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this with a secure random value

# Session configurations
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem to store sessions
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_PERMANENT'] = False  # Non-permanent sessions
app.config['SESSION_USE_SIGNER'] = True  # Sign the session cookie for security
Session(app)

# Database connection using PostgreSQL on Render
host = 'dpg-cren3f5svqrc73fkr7n0-a.oregon-postgres.render.com'
port = '5432'
database = 'realtime_screenmonitor_db'
username = 'root'
password = 'tu4nzc3K4FNTH2XWRYj3qQ3bNnjIqzXJ'

# Try to establish connection with PostgreSQL
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=password
    )
    cursor = conn.cursor()
except Exception as e:
    print(f"Error connecting to the database: {e}")

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
        cursor.execute("SELECT ID, Username, Password, IsAdmin FROM Users WHERE Username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[3]
            if user[3]:  # If the user is also an admin
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
    cursor.execute("SELECT ID, Name, Username, IsConnected FROM Users")
    users = cursor.fetchall()
    return render_template('admin_dashboard.html', users=users)

@app.route('/employee_dashboard')
def employee_dashboard():
    if not session.get('username'):
        return redirect(url_for('login'))
    cursor.execute("SELECT ID, Name, Username FROM Users WHERE Username = %s", (session['username'],))
    user = cursor.fetchone()
    return render_template('employee_dashboard.html', user=user)

@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    name = request.form['name']
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    cursor.execute("INSERT INTO Users (Name, Username, Password, IsConnected) VALUES (%s, %s, %s, 0)", (name, username, password))
    conn.commit()
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

# Route to view the screen of a user in real-time (only works in non-headless environments)
@app.route('/view_screen/<username>')
def view_screen(username):
    # You can add logic to check if the user is connected before streaming their screen
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
