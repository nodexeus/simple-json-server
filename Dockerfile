# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy application code
COPY app.py .
COPY templates/ templates/
ENV PYTHONPATH=/app

# Set environment variables
ENV PORT=3002
ENV HOST=0.0.0.0

# Expose port
EXPOSE 3002

# Run the application with gunicorn using eventlet worker for SocketIO
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:3002", "--timeout", "120", "app:app"]
