from flask import Flask, render_template, request, session, redirect, url_for

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory storage for posts and users (simulating data without a database)
users = {}
posts = []

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        if username in users:
            return "Username already exists!"
        else:
            users[username] = {"password": password, "name": name}
            session['username'] = username
            return redirect(url_for('feed'))

    return render_template('signup.html')

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('feed'))
        else:
            return 'Invalid credentials, please try again!'

    return render_template('index.html')

# Feed route (protected)
@app.route('/feed')
def feed():
    if 'username' in session:
        user = users[session['username']]
        return render_template('feed.html', user=user, posts=posts)
    return redirect(url_for('login'))

# Handle post creation
@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session:
        user = users[session['username']]
        content = request.form['content']
        new_post = {
            "author": user['name'],
            "content": content,
            "likes": 0,
            "dislikes": 0,
            "comments": [],
            "id": len(posts)
        }
        posts.append(new_post)
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

# Handle post likes
@app.route('/like/<int:post_id>')
def like_post(post_id):
    if 'username' in session:
        posts[post_id]['likes'] += 1
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

# Handle post dislikes
@app.route('/dislike/<int:post_id>')
def dislike_post(post_id):
    if 'username' in session:
        posts[post_id]['dislikes'] += 1
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

# Handle adding comments to posts
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'username' in session:
        comment = {
            "author": users[session['username']]['name'],
            "comment": request.form['comment']
        }
        posts[post_id]['comments'].append(comment)
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

# Handle post deletion
# Handle post deletion
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    global posts  # Declare global posts at the start of the function
    if 'username' in session:  # Ensure the user is logged in
        user = users[session['username']]  # Get the current user from session
        post = next((p for p in posts if p['id'] == post_id), None)  # Find the post by ID
        
        if post and post['author'] == user['name']:  # Check if the current user is the author
            posts = [p for p in posts if p['id'] != post_id]  # Remove the post from the list
            return redirect(url_for('feed'))  # Redirect to the feed after deletion
        else:
            return "You do not have permission to delete this post.", 403  # Forbidden if not the author
    return redirect(url_for('login'))  # Redirect to login if the user is not logged in


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)
