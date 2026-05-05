# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.11-slim
WORKDIR /app

# Create a non-root user
RUN groupadd -g 1000 swiftuser && \
    useradd -u 1000 -g swiftuser -s /bin/sh swiftuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/swiftuser/.local
COPY app/ .

# Ensure the logs directory exists and is writable
RUN mkdir -p /var/log/app && chown swiftuser:swiftuser /var/log/app

ENV PATH=/home/swiftuser/.local/bin:$PATH
USER swiftuser

CMD ["python", "main.py"]
