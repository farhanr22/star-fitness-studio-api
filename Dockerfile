# Builder stage ---

FROM python:3.11-slim AS builder

WORKDIR /app

# Create and activate venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .


# Final stage ---

FROM python:3.11-slim

WORKDIR /app

# Copy venv from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code from builder stage
COPY --from=builder /app .

# Set the PATH to include the venv
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]