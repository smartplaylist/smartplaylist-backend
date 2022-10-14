FROM python:3.10.7-alpine3.16
WORKDIR /api
ADD ./src/ ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "80"]
