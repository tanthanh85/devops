FROM python:3.13-slim
WORKDIR /service
COPY config-tier/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config-tier/service.py .
USER 65532:65532
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "service:app"]
