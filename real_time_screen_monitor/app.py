from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to the JSON file where user and post data will be saved
USER_DATA_FILE = 'users.json'
POST_DATA_FILE = 'posts.json'

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

# Load posts from the JSON file
def load_posts():
    if os.path.exists(POST_DATA_FILE):
        with open(POST_DATA_FILE, 'r') as file:
            return json.load(file)
    return []

# Save posts to the JSON file
def save_posts(posts):
    with open(POST_DATA_FILE, 'w') as file:
        json.dump(posts, file, indent=4)

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

            # Automatically log in the user after signup
            session['username'] = username
            return redirect(url_for('feed'))

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
@app.route('/feed', methods=['GET', 'POST'])
def feed():
    if 'username' in session:
        user = load_users()[session['username']]
        posts = load_posts()
        return render_template('feed.html', user=user, posts=posts)
    return redirect(url_for('login'))

# Create post route
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session:
        content = request.form['content']
        user = load_users()[session['username']]

        posts = load_posts()
        new_post = {
            "author": user['name'],
            "content": content,
            "likes": 0,
            "dislikes": 0,
            "comments": []
        }
        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

# Like post route
@app.route('/like/<int:post_id>', methods=['GET'])
def like_post(post_id):
    posts = load_posts()
    posts[post_id]['likes'] += 1
    save_posts(posts)
    return redirect(url_for('feed'))

# Dislike post route
@app.route('/dislike/<int:post_id>', methods=['GET'])
def dislike_post(post_id):
    posts = load_posts()
    posts[post_id]['dislikes'] += 1
    save_posts(posts)
    return redirect(url_for('feed'))

# Comment on post route
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'username' in session:
        comment = request.form['comment']
        user = load_users()[session['username']]

        posts = load_posts()
        new_comment = {"author": user['name'], "comment": comment}
        posts[post_id]['comments'].append(new_comment)
        save_posts(posts)
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
