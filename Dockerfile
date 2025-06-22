# Basis-Image mit Python
FROM python:3.12-slim

# Arbeitsverzeichnis anlegen
WORKDIR /app

# Requirements kopieren und installieren
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Dein Python-Script kopieren
COPY app.py app.py

# Starte das Script
CMD ["python", "app.py"]
