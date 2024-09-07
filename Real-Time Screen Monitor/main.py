from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change to a real secret in production
socketio = SocketIO(app)

users = {}  # Track users and their online status

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    users[username] = {'online': True}
    emit('update_users', users, broadcast=True, include_self=False)
    return jsonify(status="success", message="Logged in", username=username)

@app.route('/logout', methods=['POST'])
def logout():
    username = request.form['username']
    if username in users:
        users[username]['online'] = False
        emit('update_users', users, broadcast=True, include_self=False)
    return jsonify(status="success", message="Logged out", username=username)

@socketio.on('connect')
def handle_connect():
    emit('update_users', users, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # Assuming username can be fetched from session or passed as part of disconnect event
    username = request.args.get('username')
    if username in users:
        users[username]['online'] = False
    emit('update_users', users, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
