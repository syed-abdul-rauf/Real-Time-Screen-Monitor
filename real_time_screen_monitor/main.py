# from flask import Flask, render_template, request, redirect, session, url_for, Response
# from flask_session import Session
# import cv2
# import numpy as np
# import os

# # Import pyautogui only if we are not in a headless environment
# if 'DISPLAY' in os.environ:
#     import pyautogui
# else:
#     pyautogui = None

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Replace this with a secure random value

# # Session configurations
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_COOKIE_NAME'] = 'session'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# Session(app)

# # Hardcoded admin credentials
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "123"

# # You can also hardcode other users if needed
# users = [
#     {'id': 1, 'name': 'Admin', 'username': 'admin', 'password': '123', 'is_admin': True},
#     {'id': 2, 'name': 'John Doe', 'username': 'john', 'password': 'john123', 'is_admin': False}
# ]

# @app.route('/')
# def home():
#     return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # Check hardcoded admin credentials first
#         for user in users:
#             if username == user['username'] and password == user['password']:
#                 session['user_id'] = user['id']
#                 session['username'] = user['username']
#                 session['is_admin'] = user['is_admin']
#                 if user['is_admin']:
#                     return redirect(url_for('admin_dashboard'))
#                 else:
#                     return redirect(url_for('employee_dashboard'))

#         return render_template('login.html', error="Invalid username or password")
#     return render_template('login.html')

# @app.route('/admin_dashboard')
# def admin_dashboard():
#     if not session.get('is_admin'):
#         return redirect(url_for('login'))

#     try:
#         # Since we're not using a database, you can pass the hardcoded users to the admin dashboard
#         return render_template('admin_dashboard.html', users=users)
#     except Exception as e:
#         print(f"Error loading admin dashboard: {e}")
#         return render_template('error.html', error="Failed to load admin dashboard")

# @app.route('/employee_dashboard')
# def employee_dashboard():
#     if not session.get('username'):
#         return redirect(url_for('login'))

#     for user in users:
#         if user['username'] == session['username']:
#             return render_template('employee_dashboard.html', user=user)
    
#     return redirect(url_for('login'))

# @app.route('/add_user', methods=['GET', 'POST'])
# def add_user():
#     if not session.get('is_admin'):
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         name = request.form['name']
#         username = request.form['username']
#         password = request.form['password']

#         # Add the new user to the hardcoded users list
#         new_user = {
#             'id': len(users) + 1,
#             'name': name,
#             'username': username,
#             'password': password,
#             'is_admin': False  # By default, new users are not admin
#         }
#         users.append(new_user)

#         return redirect(url_for('admin_dashboard'))

#     return render_template('add_user.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))

# # Function to generate frames for screen capture (only works in non-headless environments)
# def generate_video_stream():
#     if pyautogui is None:
#         print("pyautogui is not available in this environment (likely headless).")
#         return b''

#     while True:
#         screenshot = pyautogui.screenshot()  # Capture screenshot
#         frame = np.array(screenshot)  # Convert the screenshot to a numpy array
#         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV compatibility
#         ret, jpeg = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
#         if not ret:
#             continue
#         # Return the frame as a byte stream for display
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# @app.route('/view_screen/<username>')
# def view_screen(username):
#     if pyautogui is None:
#         return "Screen capture is not available in this environment."
    
#     return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('error.html', error=error), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=10000)

# @app.route('/')#+
# def home():#+
#     """#+
#     Redirects the user to the login page.#+
# #+
#     This function is a route handler for the root URL ("/"). When a GET request is made to this URL,#+
#     the function redirects the user to the login page using Flask's `redirect` function and the `url_for`#+
#     function to generate the URL for the login page.#+
# #+
#     Parameters:#+
#     None#+
# #+
#     Returns:#+
#     A Flask response object that redirects the user to the login page.#+
#     """#+
#     return redirect(url_for('login'))#+
