FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıklar
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyaları
COPY . .

# Python'ın modülleri bulabilmesi için yolu tanımlıyoruz
ENV PYTHONPATH=/app

EXPOSE 8000

# API'yi modül olarak başlatmak daha sağlıklıdır
CMD ["python", "backend/api.py"]
