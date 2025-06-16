# 1. Bazowy obraz Pythona
FROM python:3.11-slim

# 2. Ustaw katalog roboczy
WORKDIR /app

# 3. Kopiuj wymagania i instaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kopiuj kod aplikacji
COPY . .

# 5. Ustaw zmienną środowiskową dla uvicorn
ENV PYTHONPATH=/app

# 6. Komenda startowa uruchamiająca FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
