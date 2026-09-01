FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal on purpose -- this is an interview/demo project.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000

# SQLite file is written to /app/data so it can be mounted as a volume
# and survive container restarts (see docker-compose.yml).
ENV DATABASE_URL=sqlite:////app/data/ecommerce.db
RUN mkdir -p /app/data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
