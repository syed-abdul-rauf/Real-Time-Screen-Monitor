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

process = None  # This will hold the process reference
users = {}  # In-memory storage for user sessions

def format_time(dt):
    return dt.strftime("%I:%M %p")

def format_duration(duration):
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
    return formatted_duration, f"{hours} hours, {minutes} minutes, {seconds} seconds"

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('monitor'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    session['username'] = username
    users[username] = {'time_in': None, 'time_out': None}
    logging.info(f"User {username} added to in-memory storage.")
    return redirect(url_for('monitor'))

@app.route('/monitor')
def monitor():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    user = users.get(username)
    if user and user['time_in']:
        time_in = format_time(user['time_in'])
        time_out = format_time(user['time_out']) if user['time_out'] else ""
        duration, breakdown = format_duration(user['time_out'] - user['time_in']) if user['time_out'] else ("", "")
        return render_template('index.html', time_in=time_in, time_out=time_out, duration=duration, breakdown=breakdown)
    return render_template('index.html')

@app.route('/logout')
def logout():
    username = session.pop('username', None)
    if username:
        logging.info(f"User {username} logged out.")
    return redirect(url_for('home'))

@app.route('/connect', methods=['POST'])
def connect():
    logging.info("Received POST request at /connect")

    if 'username' not in session:
        logging.error("No username found in session, redirecting to home.")
        return redirect(url_for('home'))

    global process
    username = session['username']

    # Ensure user exists in the in-memory storage
    if username not in users:
        logging.warning(f"User {username} not found in in-memory storage, re-adding user.")
        users[username] = {'time_in': None, 'time_out': None}

    user = users.get(username)

    if process is None:
        try:
            # Start the screen_display.py script as a subprocess and record the time_in
            time_in = datetime.datetime.now()
            user['time_in'] = time_in
            user['time_out'] = None
            process = subprocess.Popen(['python', 'screen_display.py'])
            logging.info(f"Subprocess started successfully for user {username}.")
            return jsonify(status="connected", time_in=format_time(time_in))
        except Exception as e:
            logging.error(f"Failed to start subprocess for user {username}: {e}")
            return jsonify(status="failed", error=str(e))
    else:
        # If the process is already running, just return the time_in
        logging.info(f"User {username} is already connected.")
        return jsonify(status="already connected", time_in=format_time(user['time_in']))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    logging.info("Received POST request at /disconnect")

    if 'username' not in session:
        logging.error("No username found in session, redirecting to home.")
        return redirect(url_for('home'))

    global process
    if process is not None:
        username = session['username']
        user = users.get(username)

        if user is None:
            logging.error(f"User {username} not found in in-memory storage.")
            return jsonify(status="error", message="User not found"), 404

        time_out = datetime.datetime.now()
        user['time_out'] = time_out

        # Calculate duration
        duration = time_out - user['time_in']
        formatted_duration, breakdown = format_duration(duration)

        # Terminate the screen_display.py subprocess
        process.terminate()
        process = None
        logging.info("Subprocess terminated successfully.")
        return jsonify(status="disconnected", time_out=format_time(time_out), duration=formatted_duration, breakdown=breakdown)
    else:
        logging.warning("No process was running when disconnect was requested.")
        return jsonify(status="not connected")

@app.route('/status', methods=['GET'])
def status():
    if 'username' not in session:
        logging.warning("Status requested without an active session.")
        return jsonify(running=False)

    username = session['username']
    user = users.get(username)
    if user and user['time_in']:
        logging.info(f"Status requested: User {username} is {'running' if process else 'not running'}.")
        return jsonify(running=process is not None, time_in=format_time(user['time_in']))
    return jsonify(running=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
