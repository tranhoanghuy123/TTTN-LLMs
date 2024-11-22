from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import jwt
from functools import wraps
from datetime import datetime, timedelta
app = Flask(__name__,template_folder="templates")
app.secret_key = 'supersecretkey'
# Hàm giải mã token
def decode_token(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

# Decorator kiểm tra token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        try:
            token = token.split(" ")[1]
            user_id = decode_token(token)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        return f(user_id, *args, **kwargs)
    return decorated
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
# Route để xử lý upload file
@app.route('/upload', methods=['POST'])
@token_required
def upload_file(user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = file.filename
    file_data = file.read()

    try:
        cursor = get_db_connection().cursor()
        cursor.execute(
            """
            INSERT INTO uploaded_files (filename, file_data, user_id)
            VALUES (?, ?, ?)
            """,
            (filename, file_data, user_id)
        )
        get_db_connection().commit()
        return jsonify({'message': 'File uploaded and saved to database successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route để lấy danh sách file đã tải lên
@app.route('/files', methods=['GET'])
@token_required
def get_files(user_id):
    try:
        cursor = get_db_connection().cursor()
        cursor.execute(
            """
            SELECT id, filename, upload_time 
            FROM uploaded_files 
            WHERE user_id = ?
            """,
            (user_id,)
        )
        files = cursor.fetchall()
        result = [
            {'id': row[0], 'filename': row[1], 'upload_time': row[2].strftime('%Y-%m-%d %H:%M:%S')}
            for row in files
        ]
        return jsonify({'files': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/download/<int:file_id>', methods=['GET'])
@token_required
def download_file(user_id, file_id):
    try:
        cursor = get_db_connection().cursor()
        cursor.execute(
            """
            SELECT filename, file_data 
            FROM uploaded_files 
            WHERE id = ? AND user_id = ?
            """,
            (file_id, user_id)
        )
        row = cursor.fetchone()

        if row:
            filename, file_data = row
            return (
                file_data,
                200,
                {
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Type': 'application/octet-stream',
                },
            )
        else:
            return jsonify({'error': 'File not found or access denied'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)
