import os
import re
import shutil
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from pypdf import PdfReader, PdfWriter
import uvicorn
from fastapi.staticfiles import StaticFiles
app = FastAPI()
#----problematic----
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory (sama seperti default folder Flask yaitu 'templates')
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = '../uploads/temp'
COMPRESSED_FOLDER = '../uploads/backup-folders/'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def get_date_prefix():
    """Get current date in Hari-Bulan-Tahun format"""
    now = datetime.now()
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
    sanitized = re.sub(r'[^\w\s\.-]', '', filename)
    sanitized = sanitized.replace(' ', '-')
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

# --- ENDPOINT GET: Menampilkan Halaman HTML ---
@app.get('/damaskus', response_class=HTMLResponse)
def index_view(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- ENDPOINT POST: Proses Upload & Kompresi File ---
# Menggunakan fungsi regular 'def' (bukan async def) karena ada proses I/O berat dan kompresi CPU-bound.
# FastAPI secara otomatis akan menjalankan fungsi ini di thread pool agar tidak memblokir server.
@app.post('/damaskus')
def process_upload(
    file: UploadFile = File(...),
    division: str = Form("general")
):
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={'status': 'error', 'message': 'File tidak ditemukan'}
        )

    # Buat file path temporary di folder UPLOAD_FOLDER
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        # Simpan file yang diunggah ke folder temp
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create date prefixes
        date_prefix = get_date_prefix()
        folder_prefix = get_folder_prefix()

        # Format baru: uploads/backup-folders/[DIVISI]/[BULAN-TAHUN-DIVISI]/
        division_folder = os.path.join(COMPRESSED_FOLDER, division, f"{folder_prefix}-{division}")
        os.makedirs(division_folder, exist_ok=True)

        # Sanitize original filename and create new filename
        name, ext = os.path.splitext(file.filename)
        sanitized_name = sanitize_filename(name)
        output_filename = f"{date_prefix}-{sanitized_name}{ext}"

        # Handle duplicate filenames
        output_filename = get_unique_filename(division_folder, output_filename)
        output_path = os.path.join(division_folder, output_filename)

        # --- PROSES KOMPRESI GAMBAR ---
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(filepath)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output_path, optimize=True, quality=60)

        # --- PROSES KOMPRESI PDF ---
        elif file.filename.lower().endswith('.pdf'):
            reader = PdfReader(filepath)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            for page in writer.pages:
                page.compress_content_streams()

            with open(output_path, "wb") as f:
                writer.write(f)

        else:
            shutil.move(filepath, output_path)

        # --- BAGIAN PENGHAPUSAN FILE TEMP ---
        if os.path.exists(filepath):
            os.remove(filepath)

        return {
            'status': 'success',
            'message': 'File berhasil disimpan ke struktur folder baru',
            'path': output_path
        }

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'Terjadi kesalahan: {str(e)}'
            }
        )

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=3333, reload=True)
