from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {}
posts = []

@app.route('/')
def index():
    # Always redirect to login if the user is not logged in
    if 'username' in session:
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))
        users[username] = {'name': username, 'password': password}
        session['username'] = username
        return redirect(url_for('feed'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('feed'))
        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/feed', methods=['GET'])
def feed():
    if 'username' in session:
        user = users[session['username']]
        return render_template('feed.html', user=user, posts=posts)
    return redirect(url_for('login'))  # Redirect to login if user is not logged in

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'username' in session:
        user = users[session['username']]
        content = request.form.get('content')
        if content:
            posts.append({
                'author': user['name'],
                'content': content,
                'likes': 0,
                'dislikes': 0,
                'comments': [],
                'username': session['username']
            })
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/like/<int:post_id>')
def like_post(post_id):
    if 'username' in session and post_id < len(posts):
        posts[post_id]['likes'] += 1
    return redirect(url_for('feed'))

@app.route('/dislike/<int:post_id>')
def dislike_post(post_id):
    if 'username' in session and post_id < len(posts):
        posts[post_id]['dislikes'] += 1
    return redirect(url_for('feed'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    if 'username' in session and post_id < len(posts):
        comment_content = request.form.get('comment')
        if comment_content:
            posts[post_id]['comments'].append({
                'author': users[session['username']]['name'],
                'comment': comment_content
            })
    return redirect(url_for('feed'))

if __name__ == '__main__':
    app.run(debug=True)
