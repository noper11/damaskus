import os
from flask import Flask, render_template, request, jsonify
from PIL import Image
from pypdf import PdfReader, PdfWriter
from datetime import datetime
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/temp'
COMPRESSED_FOLDER = 'uploads/backup-folders/'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def get_date_prefix():
    """Get current date in Hari-Bulan-Tahun format"""
    now = datetime.now()
    # Indonesian month names
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    hari = now.day
    bulan = months[now.month - 1]
    tahun = now.year
    return f"{hari}-{bulan}-{tahun}"

def get_folder_prefix():
    """Get current date in Bulan-Tahun format for folders"""
    now = datetime.now()
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    bulan = months[now.month - 1]
    tahun = now.year
    return f"{bulan}-{tahun}"

def sanitize_filename(filename):
    """Sanitize filename by removing special characters"""
    # Remove any characters that aren't alphanumeric, spaces, dots, or hyphens
    sanitized = re.sub(r'[^\w\s\.-]', '', filename)
    # Replace spaces with hyphens
    sanitized = sanitized.replace(' ', '-')
    # Remove multiple hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    return sanitized.strip('-')

def get_unique_filename(directory, filename):
    """Generate unique filename if duplicate exists"""
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}({counter}){ext}"
        counter += 1
    
    return new_filename

@app.route('/dms33', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        division = request.form.get('division', 'general')
        if file:
            # Create date prefixes
            date_prefix = get_date_prefix()
            folder_prefix = get_folder_prefix()
            
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            
            # Buat folder divisi dengan format Bulan-Tahun-Divisi
            division_folder_name = f"{folder_prefix}-{division}-Divisi"
            division_folder = os.path.join(COMPRESSED_FOLDER, division_folder_name)
            os.makedirs(division_folder, exist_ok=True)
            
            # Sanitize original filename and create new filename with format Hari-Bulan-Tahun-Nama-File
            name, ext = os.path.splitext(file.filename)
            sanitized_name = sanitize_filename(name)
            output_filename = f"{date_prefix}-{sanitized_name}{ext}"
            
            # Handle duplicate filenames
            output_filename = get_unique_filename(division_folder, output_filename)
            output_path = os.path.join(division_folder, output_filename)
            
            try:
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img = Image.open(filepath)
                    img.save(output_path, optimize=True, quality=60)
                elif file.filename.lower().endswith('.pdf'):
                    reader = PdfReader(filepath)
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    with open(output_path, "wb") as f:
                        writer.write(f)
                
                # --- BAGIAN PENGHAPUSAN FILE ---
                if os.path.exists(filepath):
                    os.remove(filepath)
                # -------------------------------
                
                return jsonify({
                    'status': 'success',
                    'message': f'File berhasil disimpan',
                    'path': output_path
                })
            
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Terjadi kesalahan: {str(e)}'
                })
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="3333", debug=True)
