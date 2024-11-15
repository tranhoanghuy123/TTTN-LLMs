from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc

app = Flask(__name__,template_folder="templates")
app.secret_key = 'supersecretkey'

# Kết nối tới cơ sở dữ liệu SQL Server
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-G9HGJRS\\SQLEXPRESS;'
        'DATABASE=Project_TTTN;'
        'UID=sa;'
        'PWD=123456a@;'
        'TrustServerCertificate=yes'
    )
    return conn

# Route trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Đăng ký thành công! Bạn có thể đăng nhập.')
            return redirect(url_for('login'))
        except pyodbc.IntegrityError:
            flash('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.')
        finally:
            conn.close()

    return render_template('register.html')

# Route trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!')

    return render_template('login.html')

# Route trang chính sau khi đăng nhập
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')

# Route đăng xuất
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Bạn đã đăng xuất!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,port=8080,use_reloader=False)
