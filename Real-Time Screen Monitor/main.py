from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
socketio = SocketIO(app)

# Dummy user management
users = {}

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
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/connect', methods=['POST'])
def connect():
    if 'username' not in session:
        return jsonify(status="error", error="No user logged in")

    username = session['username']
    if users[username]['time_in'] is None:
        users[username]['time_in'] = datetime.datetime.now()
        socketio.emit('status', {'user': username, 'action': 'connected'}, broadcast=True)
        return jsonify(status="connected", time_in=users[username]['time_in'].strftime("%I:%M %p"))
    else:
        return jsonify(status="already connected")

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if 'username' not in session:
        return jsonify(status="error", error="No user logged in")

    username = session['username']
    if users[username]['time_in'] is not None:
        users[username]['time_out'] = datetime.datetime.now()
        duration = users[username]['time_out'] - users[username]['time_in']
        users[username]['time_in'] = None
        socketio.emit('status', {'user': username, 'action': 'disconnected'}, broadcast=True)
        return jsonify(status="disconnected", duration=str(duration))
    else:
        return jsonify(status="not connected")

@socketio.on('message')
def handle_message(message):
    print('Received message: ' + message)
    socketio.send('Echo: ' + message)

if __name__ == '__main__':
    socketio.run(app, debug=True)
