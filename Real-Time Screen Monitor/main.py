from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for session management
socketio = SocketIO(app, cors_allowed_origins='*')  # Allow all origins for simplicity

users = {}  # Storing user data in memory

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('monitor'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    session['username'] = username
    users[username] = {'time_in': datetime.datetime.now(), 'time_out': None}
    return redirect(url_for('monitor'))

@app.route('/monitor')
def monitor():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    return render_template('monitor.html', username=username)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@socketio.on('connect')
def on_connect():
    print('User connected:', request.sid)
    emit('server_response', {'data': 'Connected to server'})

@socketio.on('disconnect')
def on_disconnect():
    print('User disconnected:', request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
