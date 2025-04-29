from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import os
import base64
from hashlib import sha256

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.secret_key = 'your-secret-key-here'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def generate_key(password):
    # Convert password to 32-byte key and base64 encode it
    hashed = sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    password = request.form.get('password')

    if file.filename == '' or not password:
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    key = generate_key(password)
    cipher = Fernet(key)

    with open(filepath, 'rb') as f:
        file_data = f.read()

    encrypted_data = cipher.encrypt(file_data)

    encrypted_filename = f"encrypted_{filename}"
    encrypted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
    with open(encrypted_filepath, 'wb') as f:
        f.write(encrypted_data)

    os.remove(filepath)

    return send_file(
        encrypted_filepath,
        as_attachment=True,
        download_name=encrypted_filename
    )

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    password = request.form.get('password')

    if file.filename == '' or not password:
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        key = generate_key(password)
        cipher = Fernet(key)

        with open(filepath, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        decrypted_filename = f"decrypted_{filename}"
        decrypted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)
        with open(decrypted_filepath, 'wb') as f:
            f.write(decrypted_data)

        os.remove(filepath)

        return send_file(
            decrypted_filepath,
            as_attachment=True,
            download_name=decrypted_filename
        )

    except Exception as e:
        os.remove(filepath)
        return f"Decryption failed: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)
