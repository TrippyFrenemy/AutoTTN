FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

ENV PORT=8000
EXPOSE $PORT

# Make the migrations script+ executable

CMD alembic revision
CMD alembic revision --autogenerate
CMD alembic upgrade head
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT