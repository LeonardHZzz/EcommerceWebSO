FROM python:3.12-slim

# PyMySQL es puro Python (sin extensiones nativas que compilar) y
# "cryptography" ya trae wheels precompilados para este entorno, así que
# no hace falta gcc ni libpq-dev/libmysqlclient-dev aquí. Se deja "curl"
# por si luego lo necesitas para healthchecks o debugging dentro del contenedor.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Gunicorn con workers Uvicorn: patrón estándar para producción en Azure
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120"]
