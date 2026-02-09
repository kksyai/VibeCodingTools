FROM python:3.11-slim

WORKDIR /app

# Install API dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install bot dependencies
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r bot/requirements.txt

# Copy API files
COPY api/ .

# Copy bot files
COPY bot/ .

# Copy data files
COPY data/ ./data/

ENV PORT=8000
ENV API_BASE_URL=http://0.0.0.0:8000

EXPOSE 8000

# Run both API and bot
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT & python3 bot/bot.py"]