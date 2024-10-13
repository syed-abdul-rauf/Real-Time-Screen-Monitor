from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to the JSON file where user data will be saved
USER_DATA_FILE = 'users.json'

# Load user data from the JSON file
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save user data to the JSON file
def save_users(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        users = load_users()

        if username in users:
            return "Username already exists!"
        else:
            # Save the new user to the JSON file
            users[username] = {"password": password, "name": name}
            save_users(users)
            return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('feed'))
        else:
            return 'Invalid credentials, please try again!'

    return render_template('index.html')

# Feed route (protected, only accessible when logged in)
@app.route('/feed')
def feed():
    if 'username' in session:
        user = load_users()[session['username']]
        return f"Welcome {user['name']} to your feed!"
    return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
