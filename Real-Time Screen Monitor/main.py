from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('Received message: ' + str(data))
    emit('response', {'data': 'Server received: ' + str(data)})

if __name__ == '__main__':
    socketio.run(app, debug=True)


# from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from flask_socketio import SocketIO
# import subprocess
# import os
# import datetime
# import logging

# app = Flask(__name__)
# app.secret_key = os.urandom(24)  # Secret key for session management
# socketio = SocketIO(app)

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# process = None  # This will hold the process reference

# def format_time(dt):
#     return dt.strftime("%I:%M %p")

# def format_duration(duration):
#     total_seconds = int(duration.total_seconds())
#     hours, remainder = divmod(total_seconds, 3600)
#     minutes, seconds = divmod(remainder, 60)
#     formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
#     return formatted_duration, f"{hours} hours, {minutes} minutes, {seconds} seconds"

# @app.route('/')
# def home():
#     if 'username' in session:
#         return redirect(url_for('monitor'))
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     session['username'] = username
#     return redirect(url_for('monitor'))

# @app.route('/monitor')
# def monitor():
#     if 'username' not in session:
#         return redirect(url_for('home'))
#     username = session['username']
#     return render_template('index.html', username=username)

# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('home'))

# @app.route('/connect', methods=['POST'])
# def connect():
#     if 'username' not in session:
#         return redirect(url_for('home'))
#     global process
#     if process is None:
#         process = subprocess.Popen(['python', 'screen_display.py'])
#         logging.info("Subprocess started successfully.")
#         return jsonify(status="connected")
#     else:
#         return jsonify(status="already connected")

# @app.route('/disconnect', methods=['POST'])
# def disconnect():
#     global process
#     if process is not None:
#         process.terminate()
#         process = None
#         logging.info("Subprocess terminated successfully.")
#         return jsonify(status="disconnected")
#     else:
#         return jsonify(status="not connected")

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000)
