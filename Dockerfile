FROM python:3.9-slim

# Tesseract ကို သွင်းမယ်
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Flask app ကို run မယ့် command
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]