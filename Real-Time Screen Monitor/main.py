from flask import Flask, render_template, request, redirect, session, url_for, Response
import cv2
import pyautogui
import numpy as np
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this with a secure random value
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database connection using Windows Authentication
server = 'LAPTOP-ECFADG26\\SQLEXPRESS'
database = 'realtime_screenmonitor_db'
cnxn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
cursor = cnxn.cursor()

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
        cursor.execute("SELECT ID, Username, Password, IsAdmin FROM Users WHERE Username = ?", username)
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
    cursor.execute("SELECT ID, Name, Username FROM Users WHERE Username = ?", session['username'])
    user = cursor.fetchone()
    return render_template('employee_dashboard.html', user=user)

@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    name = request.form['name']
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    cursor.execute("INSERT INTO Users (Name, Username, Password, IsConnected) VALUES (?, ?, ?, 0)", (name, username, password))
    cnxn.commit()
    return redirect(url_for('admin_dashboard'))

# Function to generate frames for screen capture
def generate_video_stream():
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

# Route to view the screen of a user in real-time
@app.route('/view_screen/<username>')
def view_screen(username):
    # You can add logic to check if the user is connected before streaming their screen
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
