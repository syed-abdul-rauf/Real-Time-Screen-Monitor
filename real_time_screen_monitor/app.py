from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simulated user database
users = {
    "john_doe": {"password": "password123", "name": "John Doe", "friends": ["jane_doe"]},
    "jane_doe": {"password": "password456", "name": "Jane Doe", "friends": ["john_doe"]}
}

# Simulated post database
posts = []

# Index page (Login page)
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('feed'))
    return render_template('index.html')

# Signup page route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        if username in users:
            return "Username already exists!"
        else:
            users[username] = {"password": password, "name": name, "friends": []}
            return redirect(url_for('index'))
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('feed'))
    else:
        return 'Invalid credentials, please try again!'

# Feed page (where posts will be displayed)
@app.route('/feed')
def feed():
    if 'username' in session:
        user = users[session['username']]
        return render_template('feed.html', user=user, posts=posts)
    return redirect(url_for('index'))

# Route for creating a new post
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session:
        user = session['username']
        content = request.form['content']
        
        post = {
            "author": user,
            "content": content,
            "likes": 0,
            "dislikes": 0,
            "comments": []
        }
        posts.insert(0, post)  # Insert at the top of the feed
        return redirect(url_for('feed'))
    return redirect(url_for('index'))

# Route for liking a post
@app.route('/like/<int:post_id>')
def like_post(post_id):
    if 'username' in session:
        if post_id < len(posts):
            posts[post_id]['likes'] += 1
        return redirect(url_for('feed'))
    return redirect(url_for('index'))

# Route for disliking a post
@app.route('/dislike/<int:post_id>')
def dislike_post(post_id):
    if 'username' in session:
        if post_id < len(posts):
            posts[post_id]['dislikes'] += 1
        return redirect(url_for('feed'))
    return redirect(url_for('index'))

# Route for commenting on a post
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'username' in session:
        if post_id < len(posts):
            comment = request.form['comment']
            posts[post_id]['comments'].append({
                "author": session['username'],
                "comment": comment
            })
        return redirect(url_for('feed'))
    return redirect(url_for('index'))

# Profile page
@app.route('/profile/<username>')
def profile(username):
    if 'username' in session and username in users:
        user_profile = users[username]
        return render_template('profile.html', user_profile=user_profile)
    return redirect(url_for('index'))

# Logout functionality
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)