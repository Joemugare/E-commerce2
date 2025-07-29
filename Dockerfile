FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=100
COPY . .
ENV DJANGO_SETTINGS_MODULE=store_project.settings
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "store_project.wsgi"]