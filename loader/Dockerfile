FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY load_csvs.py .

ENV LANDING_DIR=/data/landing
ENV DB_PATH=/data/warehouse/retail_data.db

CMD ["python", "load_csvs.py"]
