FROM python:3.11-slim AS builder

WORKDIR /app

COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app /app
COPY ./app .

CMD ["streamlit", "run", "app.py"]



