from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import os
import datetime
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

logging.basicConfig(level=logging.INFO)

process = None
users = {}

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
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/connect', methods=['POST'])
def connect():
    if 'username' not in session:
        return redirect(url_for('home'))

    global process
    username = session['username']
    user = users[username]

    if process is None:
        try:
            time_in = datetime.datetime.now()
            user['time_in'] = time_in
            user['time_out'] = None
            process = subprocess.Popen(['python', 'screen_display.py'])
            logging.info("Subprocess started successfully.")
            return jsonify(status="connected", time_in=format_time(time_in))
        except Exception as e:
            logging.error(f"Failed to start subprocess: {e}")
            return jsonify(status="failed", error=str(e))
    else:
        return jsonify(status="already connected", time_in=format_time(user['time_in']))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if 'username' not in session:
        return redirect(url_for('home'))

    global process
    if process is not None:
        username = session['username']
        user = users[username]
        time_out = datetime.datetime.now()
        user['time_out'] = time_out

        duration = time_out - user['time_in']
        formatted_duration, breakdown = format_duration(duration)

        process.terminate()
        process = None
        logging.info("Subprocess terminated successfully.")
        return jsonify(status="disconnected", time_out=format_time(time_out), duration=formatted_duration, breakdown=breakdown)
    else:
        return jsonify(status="not connected")

@socketio.on('connect')
def handle_connect():
    emit('response', {'message': 'Connected to WebSocket!'})

@socketio.on('screen_data')
def handle_screen_data(data):
    emit('screen_update', {'image': data}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
