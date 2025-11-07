# Dev et prod

## backend/Dockerfile
FROM python:3.11-slim AS dev

# Qualité de logs / comportement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Installe ce dont on a besoin
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copie le code (sera surchargé par le volume en dev)
COPY backend /app

# Variables dev Flask
ENV FLASK_APP=wsgi.py FLASK_ENV=development

# Démarre le serveur de dev Flask - hotload
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]
