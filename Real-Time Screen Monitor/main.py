from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
import pyodbc
import subprocess
import os
import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
socketio = SocketIO(app)

# SQL Server connection configuration using pyodbc
connection_string = 'DRIVER={SQL Server};SERVER=LAPTOP-ECFADG26\\SQLEXPRESS;DATABASE=Real-Time Screen Monitor;Trusted_Connection=yes;'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Ensure the users415 table exists with password support
def create_users_table():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users415' AND xtype='U')
                CREATE TABLE users415 (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    username NVARCHAR(80) NOT NULL UNIQUE,
                    password_hash NVARCHAR(255) NOT NULL,
                    time_in DATETIME NULL,
                    time_out DATETIME NULL
                );
            ''')
            conn.commit()
            logging.info("Users table 'users415' created or already exists.")
    except Exception as e:
        logging.error(f"Error creating users table: {e}")

create_users_table()

process = None  # This will hold the process reference

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
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users415 WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user:
                if check_password_hash(user[0], password):
                    session['username'] = username
                    logging.info(f"User {username} logged in successfully.")
                    return redirect(url_for('monitor'))
                else:
                    logging.info("Password is incorrect.")
                    return "Password is incorrect", 401
            else:
                cursor.execute("INSERT INTO users415 (username, password_hash) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                session['username'] = username
                logging.info(f"New user {username} added to the database with hashed password.")
                return redirect(url_for('monitor'))
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return str(e), 500

@app.route('/monitor')
def monitor():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT time_in, time_out FROM users415 WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and user[0]:
                time_in = format_time(user[0])
                time_out = format_time(user[1]) if user[1] else ""
                duration, breakdown = format_duration(user[1] - user[0]) if user[1] else ("", "")
                return render_template('index.html', time_in=time_in, time_out=time_out, duration=duration, breakdown=breakdown)
            else:
                logging.info(f"No session data found for user {username}.")
                return render_template('index.html', time_in="", time_out="", duration="", breakdown="")
    except Exception as e:
        logging.error(f"Error retrieving session data: {e}")
        return str(e), 500

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

    if process is None:
        try:
            time_in = datetime.datetime.now()
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users415 SET time_in = ?, time_out = NULL WHERE username = ?", (time_in, username))
                conn.commit()
                logging.info(f"User {username} connected at {time_in}.")
                
            process = subprocess.Popen(['python', 'screen_display.py'])
            logging.info("Subprocess started successfully.")
            return jsonify(status="connected", time_in=format_time(time_in))
        except Exception as e:
            logging.error(f"Failed to start subprocess or update database: {e}")
            return jsonify(status="failed", error=str(e))
    else:
        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT time_in FROM users415 WHERE username = ?", (username,))
                user = cursor.fetchone()
                if user:
                    return jsonify(status="already connected", time_in=format_time(user[0]))
        except Exception as e:
            logging.error(f"Error checking connection status: {e}")
        return jsonify(status="error")

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if 'username' not in session:
        return redirect(url_for('home'))

    global process
    if process is not None:
        username = session['username']
        time_out = datetime.datetime.now()

        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users415 SET time_out = ? WHERE username = ?", (time_out, username))
                conn.commit()
                logging.info(f"User {username} disconnected at {time_out}.")

                cursor.execute("SELECT time_in FROM users415 WHERE username = ?", (username,))
                time_in = cursor.fetchone()
                if time_in is None:
                    logging.error(f"No time_in found for user {username}.")
                    return jsonify(status="error", error="No time_in found")

                duration = time_out - time_in[0]
                formatted_duration, breakdown = format_duration(duration)

            process.terminate()
            process = None
            logging.info("Subprocess terminated successfully.")
            return jsonify(status="disconnected", time_out=format_time(time_out), duration=formatted_duration, breakdown=breakdown)
        except Exception as e:
            logging.error(f"Error during disconnection: {e}")
            return jsonify(status="failed", error=str(e))
    else:
        return jsonify(status="not connected")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)  # Ensure you're using an available port
