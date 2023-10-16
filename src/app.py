from flask import Flask, flash, g, render_template, session, request, redirect, url_for
import sqlite3

app = Flask(__name__, static_url_path='/static')
app.secret_key = "scAHj4MW1R"
# Define the path to your SQLite database file
DATABASE = 'D:\\16_Projects\\AutoScan\\data\\data.sqlite'

# Function to create a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Function to execute a query and return the results as a dictionary
def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    results = cur.fetchall()
    conn.close()
    return (results[0] if results else None) if one else results

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/display_tables', methods = ['GET', 'POST'])
def display_data():
    # print(session)
    if not 'user_id' in session:
        return redirect('/login')
    if request.method == 'POST':
        id = request.form['code']
        vehicle_section = id[0]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT desc FROM codes WHERE id = ?", [id])
        data = cursor.fetchone()
        if data:
            return render_template('display_tables.html', data = data[0], vehicle_section=vehicle_section)
        else:
            return render_template('display_tables.html', data = "Code not found")

    return render_template('display_tables.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(session)
    session['logged_in'] = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            flash('Login successful!')
            return redirect('/display_tables')
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request)
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        # Check if the username already exists in the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('signup.html', error=error)
        else:
            # Insert the new user into the database
            cursor.execute("INSERT INTO users (name, username, password) VALUES (?, ?, ?)", (name, username, password))
            conn.commit()
            conn.close()
            flash('Signup successful! You can now login.')
            return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect('/login')

@app.route('/')
def redirect_to_login():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
    

