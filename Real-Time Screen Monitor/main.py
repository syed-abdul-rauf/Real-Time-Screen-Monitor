from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import os
import datetime
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Randomly generate a secret key
socketio = SocketIO(app)

logging.basicConfig(level=logging.INFO)

process = None
users = {}  # In-memory storage to manage user sessions

def format_time(dt):
    """ Helper function to format datetime objects to a readable time format. """
    return dt.strftime("%I:%M %p")

@app.route('/')
def home():
    """ Home route that redirects to the monitor page if the user is logged in. """
    if 'username' in session:
        return redirect(url_for('monitor'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """ Handles user login, initializing user data in the in-memory dictionary. """
    username = request.form['username']
    session['username'] = username
    users[username] = {'time_in': datetime.datetime.now(), 'time_out': None}
    return redirect(url_for('monitor'))

@app.route('/monitor')
def monitor():
    """ Monitor page displaying the user's session times if logged in. """
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    user = users[username]
    time_in = format_time(user['time_in'])
    time_out = format_time(user['time_out']) if user['time_out'] else "N/A"
    return render_template('index.html', time_in=time_in, time_out=time_out)

@app.route('/logout')
def logout():
    """ Log out the user and clear their session. """
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/connect', methods=['POST'])
def connect():
    """ Endpoint to handle the start of a screen-sharing session. """
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    user = users[username]

    if not process:
        try:
            user['time_in'] = datetime.datetime.now()
            user['time_out'] = None
            # Assume screen_display.py is a script to capture and send the screen data
            process = subprocess.Popen(['python', 'screen_display.py'])
            logging.info("Subprocess started successfully.")
            return jsonify(status="connected", time_in=format_time(user['time_in']))
        except Exception as e:
            logging.error(f"Failed to start subprocess: {e}")
            return jsonify(status="failed", error=str(e))
    else:
        return jsonify(status="already connected", time_in=format_time(user['time_in']))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    """ Handles the termination of a screen-sharing session. """
    if 'username' not in session:
        return redirect(url_for('home'))

    global process
    username = session['username']
    user = users[username]
    user['time_out'] = datetime.datetime.now()

    if process:
        process.terminate()
        process = None
        logging.info("Subprocess terminated successfully.")
        duration = user['time_out'] - user['time_in']
        formatted_duration = format_time(duration)
        return jsonify(status="disconnected", time_out=format_time(user['time_out']), duration=formatted_duration)
    else:
        return jsonify(status="not connected")

@socketio.on('connect')
def handle_connect():
    """ Notifies user of connection to the WebSocket. """
    emit('response', {'message': 'You are connected to WebSocket!'})

@socketio.on('screen_data')
def handle_screen_data(data):
    """ Handles incoming screen data and broadcasts it to all clients. """
    emit('screen_update', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
