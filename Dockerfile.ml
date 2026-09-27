FROM python:3.12-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic
COPY ml_service.py .
CMD ["uvicorn", "ml_service:app", "--host", "0.0.0.0", "--port", "8001"]
