# ============================================
# BOTFUSIONS - MEMORI API DOCKERFILE
# ============================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="info@botfusions.com"
LABEL description="Memori API Service for Botfusions"

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Non-root user
RUN useradd -m -u 1000 memori && chown -R memori:memori /app
USER memori

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')"

# Port
EXPOSE 8002

# Başlat
CMD ["uvicorn", "memori_api:app", "--host", "0.0.0.0", "--port", "8002"]
