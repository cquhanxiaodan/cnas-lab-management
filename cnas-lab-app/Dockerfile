FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

WORKDIR /app/backend

ENV DATABASE_URL=sqlite:///./data/cnas_lab.db
ENV UPLOAD_DIR=./uploads
ENV SECRET_KEY=cnas-lab-secret-key-change-in-production

RUN mkdir -p /app/backend/data /app/backend/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
