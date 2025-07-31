FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY exporter.py ./
COPY templates/ templates/

CMD ["python", "exporter.py"]
