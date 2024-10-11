import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '12345'  # For session management

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'muka_enterprises'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Route for admin/user login

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        cursor = mysql.cursor(pymysql.cursors.DictCursor)

        if user_type == 'admin':
            cursor.execute('SELECT * FROM admin WHERE username = %s', (username,))
        else:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        
        user = cursor.fetchone()

        if user:
            # Check password
            if user['password'] == password:
                session['loggedin'] = True
                session['username'] = user['username']

                if user_type == 'admin':
                    return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
                else:
                    return redirect(url_for('home_page'))  # Redirect to user home page
            else:
                error = 'Invalid password.'
        else:
            error = 'Username not found.'
    
    return render_template('admin_login.html', error=error, current_year=datetime.datetime.now().year)

# Route for admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session:
        return render_template('admin_dashboard.html', username=session['username'])
    return redirect(url_for('admin_login'))

# Route to logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('admin_login'))
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
