FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt src/requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

COPY src/backend src/backend
COPY src/DataRef src/DataRef
RUN mkdir -p src/data/model

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
