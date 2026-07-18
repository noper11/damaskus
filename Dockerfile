FROM python:3.11-slim

WORKDIR /app

# Salin isi dari folder 'app' ke root container '/app'
COPY app/ .
# Salin requirements.txt
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3333

# Sekarang main.py berada tepat di /app/main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3333"]
