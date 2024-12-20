FROM python:3.9-slim

WORKDIR /crawler
COPY . /crawler
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy requirements first to leverage Docker cache
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV PYTHONPATH=/crawler

# Copy the .env file
COPY .env .

# Copy the rest of the application
COPY . .

CMD ["python", "-m", "airflow.app.main"]

