FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema mínimas para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copia del código (se sobrescribirá con bind mount en compose durante desarrollo)
COPY ./app /app

# Puerto por defecto de Flask
EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
