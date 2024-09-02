from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
import subprocess
import os
import datetime
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

users = {}  # Using a simple dictionary to manage users for demonstration

process = None  # This will hold the process reference

def format_time(dt):
    return dt.strftime("%I:%M %p")

def format_duration(start, end):
    duration = end - start
    hours, remainder = divmod(int(duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}", f"{hours} hours, {minutes} minutes, {seconds} seconds"

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('monitor'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']  # Assuming password handling is added
    session['username'] = username
    users[username] = {'time_in': None, 'time_out': None}
    logging.info(f"User {username} added or updated in session.")
    return redirect(url_for('monitor'))

@app.route('/monitor')
def monitor():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    user_data = users.get(username, {})
    if user_data and user_data['time_in']:
        time_in = format_time(user_data['time_in'])
        time_out = format_time(user_data['time_out']) if user_data['time_out'] else ""
        duration, breakdown = format_duration(user_data['time_in'], user_data['time_out']) if user_data['time_out'] else ("", "")
        return render_template('index.html', time_in=time_in, time_out=time_out, duration=duration, breakdown=breakdown)
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/connect', methods=['POST'])
def connect():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    users[username]['time_in'] = datetime.datetime.now()
    global process
    if process is None:
        process = subprocess.Popen(['python', 'screen_display.py'])  # Launch screen display
        logging.info("Subprocess started successfully.")
    return jsonify(status="connected", time_in=format_time(users[username]['time_in']))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    users[username]['time_out'] = datetime.datetime.now()
    if process:
        process.terminate()
        process = None
        logging.info("Subprocess terminated successfully.")
    time_in = users[username]['time_in']
    time_out = users[username]['time_out']
    duration, breakdown = format_duration(time_in, time_out)
    return jsonify(status="disconnected", time_out=format_time(time_out), duration=duration, breakdown=breakdown)

@app.route('/status', methods=['GET'])
def status():
    if 'username' not in session:
        return jsonify(running=False)
    username = session['username']
    return jsonify(running=process is not None, time_in=format_time(users[username]['time_in']))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
