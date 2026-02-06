FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --timeout=600 -r requirements.txt

COPY app ./app

CMD ["python", "app/worker.py"]
