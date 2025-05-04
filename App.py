from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
import random
import string

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/code_auth'
db = SQLAlchemy(app)

# Upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024  # 100 GB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'careseniore@gmail.com'
app.config['MAIL_PASSWORD'] = 'dkig aier ifao rkrn'
mail = Mail(app)

class Code(db.Model):
    __tablename__ = 'codes'
    id = db.Column(db.Integer, primary_key=True)
    code_hash = db.Column(db.String(255), nullable=False)
    plain_code = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    code_id = db.Column(db.Integer, db.ForeignKey('codes.id'), nullable=False)
    code = db.relationship('Code', backref=db.backref('files', lazy=True))

def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_code = request.form.get('code')
        if not entered_code:
            return render_template('login.html', error="Please enter code.")

        code_entry = Code.query.filter_by(plain_code=entered_code).first()
        if code_entry and check_password_hash(code_entry.code_hash, entered_code):
            session['authenticated'] = True
            session['code_id'] = code_entry.id
            return redirect(url_for('transferQaulipro'))

        return render_template('login.html', error="Invalid code.")

    return render_template('login.html')

@app.route('/transferQaulipro', methods=['GET', 'POST'])
def transferQaulipro():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    code_id = session['code_id']
    code_entry = Code.query.get(code_id)

    if request.method == 'POST':
        uploaded_file = request.files['file']
        recipient_email = request.form.get('email')

        if not uploaded_file or not recipient_email:
            flash('Please provide both file and email.', 'danger')
            return redirect(url_for('transferQaulipro'))

        # Generate new code
        new_plain_code = generate_random_code(8)
        code_hash = generate_password_hash(new_plain_code)

        # Save code to DB
        new_code = Code(plain_code=new_plain_code, code_hash=code_hash, email=recipient_email)
        db.session.add(new_code)
        db.session.commit()

        # Create folder
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], new_plain_code)
        os.makedirs(folder_path, exist_ok=True)

        # Save file
        file_path = os.path.join(folder_path, uploaded_file.filename)
        uploaded_file.save(file_path)

        # Save file record in DB
        new_file = File(filename=uploaded_file.filename, code_id=new_code.id)
        db.session.add(new_file)
        db.session.commit()

        # Send email with code
        msg = Message('Your Access Code', sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
        msg.body = f'Your access code to download your file is: {new_plain_code}'
        mail.send(msg)

        flash('File uploaded, code generated and email sent!', 'success')
        return redirect(url_for('transferQaulipro'))

    # Load files depending on code
    folder_code = code_entry.plain_code
    files = []
    if folder_code == '123456':
        folders = os.listdir(app.config['UPLOAD_FOLDER'])
        for folder in folders:
            folder_files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], folder))
            files.extend([f"{folder}/{fname}" for fname in folder_files])
    else:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_code)
        if os.path.exists(folder_path):
            files = [f"{folder_code}/{f}" for f in os.listdir(folder_path)]

    return render_template('transferQaulipro.html', files=files, default_code=(folder_code == '123456'))


@app.route('/uploads/<path:filepath>')
def download_file(filepath):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'])
    absolute_file_path = os.path.join(folder_path, filepath)

    if not os.path.exists(absolute_file_path):
        return "File not found!", 404

    directory = os.path.dirname(absolute_file_path)
    filename = os.path.basename(absolute_file_path)

    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/delete/<path:filepath>', methods=['POST'])
def delete_file(filepath):
    # Get the folder path containing the uploaded file
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'])
    absolute_file_path = os.path.join(folder_path, filepath)

    # Get the directory of the file to delete all files and the folder itself
    file_directory = os.path.dirname(absolute_file_path)

    if os.path.exists(file_directory):
        # Delete all files in the folder
        for filename in os.listdir(file_directory):
            file_path = os.path.join(file_directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # After deleting the files, remove the folder itself
        os.rmdir(file_directory)

        flash('Folder and all files have been deleted successfully.', 'success')
    else:
        flash('Folder not found.', 'danger')

    return redirect(url_for('transferQaulipro'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
