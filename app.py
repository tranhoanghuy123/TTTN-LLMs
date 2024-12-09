import os
import re
import cv2
import multiprocessing as mp
import uuid
import pytesseract
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from views.regex_pattern import patterns
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
from datetime import datetime
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" #Path cai dat tesseract
# create a Flask app instance
app = Flask(__name__)
app.secret_key = 'supersecretkey'
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-G9HGJRS\\SQLEXPRESS;'
        'DATABASE=Project_TTTN;'
        'UID=sa;'
        'PWD=123456;'
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
            flash('Đăng nhập thành công!')
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
# configure the app
app.config['UPLOAD_FOLDER'] = 'UPLOAD'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['MAX_FILES'] = 10  # So luong file co the upload toi da tai 1 thoi diem

# -----------------------------------------------------------------------------------------------------
def is_image_file(filename):
    """Check if a file is an image file based on its extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']



# -----------------------------------------------------------------------------------------------------
def generate_unique_filename(filename):
    """Generate a unique filename for an uploaded file."""
    # get the file extension
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    # generate a random UUID and use it as the new filename
    new_filename = f"{str(uuid.uuid4())}.{ext}"
    return new_filename


# -----------------------------------------------------------------------------------------------------
def process_file(input_image_path):
    """Perform OCR on an image file and extract field values using regular expressions."""
    image = cv2.imread(input_image_path)
    invoice_text = pytesseract.image_to_string(image)

    # khoi tao tu dien rong de luu gia tri
    fields = {}

    # trich xuat gia tri cua toan bo pattern
    for key, pattern in patterns.items():
        match = re.search(pattern, invoice_text)
        if match:
            fields[key] = match.group(1).strip()

    # tra ve cac truong da trich xuat va ten tep

    if not fields:
        return os.path.basename(input_image_path), 'Day khong phai la anh hoa don'
    else:
        # return the extracted fields and the file name
        return os.path.basename(input_image_path), fields
def SaveFileToDB(filename):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print ('\\UPLOAD\\'+ filename)
        print (str(session['user_id']))
        cursor.execute("INSERT INTO uploaded_files (pathFile, UserId) VALUES (?, ?)",('UPLOAD/'+ filename, session['user_id']))
        conn.commit()
        print ('Created')
        return jsonify({'message': 'File uploaded and saved to database successfully!'}), 200

    except Exception as e:
        print (' Dont Create')
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload', methods=['POST'])
def upload():
    """Handle file uploads and process them using multiprocessing."""
    # check if any files were submitted
    if 'files[]' not in request.files:
        return jsonify({'error': 'Không có file nào được tải lên'})

    # get the list of files submitted
    files = request.files.getlist('files[]')

    # check if the number of files is within the allowed limit
    if len(files) > app.config['MAX_FILES']:
        return jsonify({'error': f"Maximum {app.config['MAX_FILES']} files are allowed at a time"})

    # check if each file is an image file and within the size limit
    for file in files:
        if not is_image_file(file.filename):
            return jsonify({'error': f"{file.filename} Đây không phải ảnh hóa đơn"})

        if file.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': f"{file.filename} dung lượng ảnh quá lớn(>5MB)"})

    # create the input directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # save the files to the input directory and create a list of their filenames
    filenames = []
    for file in files:
        filename = generate_unique_filename(file.filename)
        fileNameUploaded = str(session['user_id']) +'_'+str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'_'+ filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],fileNameUploaded ))
        SaveFileToDB(fileNameUploaded)
        filenames.append(fileNameUploaded)
    # process the files using multiprocessing
    pool = mp.Pool(processes=len(filenames))
    results = [pool.apply_async(process_file, args=(os.path.join(app.config['UPLOAD_FOLDER'], fileNameUploaded),)) for fileNameUploaded in filenames]
    fields_list = [result.get() for result in results]
    pool.close()
    pool.join()

    # create a dictionary of extracted fields and their associated file names
    response = {}
    for i in range(len(filenames)):
        response[filenames[i]] = fields_list[i][1]

    # return the extracted fields and file names as JSON
    return jsonify({'fields': response})

# -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

