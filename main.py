import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Database setup
DATABASE = 'username.db'

# Rebuild the database (optional)
try:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("VACUUM")  # Attempts to rebuild the database
    print("Database vacuumed successfully.")
except sqlite3.DatabaseError as e:
    print(f"Error: {e}")
    
def init_db():
    """Initialize the database and create the users table if it doesn't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                age INTEGER NOT NULL,
                address TEXT
            )
        """)
        conn.commit()

# Initialize the database
init_db()

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        age = int(request.form['age'])  # Convert age to integer
        address = request.form.get('address', '')  # Optional field

        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Insert user into the database
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, email, phone, age, address) VALUES (?, ?, ?, ?, ?, ?)", 
                               (username, hashed_password, email, phone, age, address))
                conn.commit()
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists. Please choose a different one.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists in the database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row and check_password_hash(row[0], password):  # Compare hash
                session['username'] = username  # Store username in session
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')  # Flash an error message
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']  # Retrieve username from session
        return render_template('dashboard.html', username=username)
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))
    
@app.route('/tutorial')
def tutorial():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']  # Retrieve username from session
        return render_template('tutorial.html', username=username)
    
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

@app.route('/broker')
def broker():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']  # Retrieve username from session
        return render_template('broker.html', username=username)
    
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()  # Remove username from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
