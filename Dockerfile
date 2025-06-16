# 1. Bazowy obraz Pythona
FROM python:3.11-slim

# 2. Ustaw katalog roboczy
WORKDIR /app

# 3. Kopiuj wymagania i instaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kopiuj cały katalog 'app'
COPY app ./app
