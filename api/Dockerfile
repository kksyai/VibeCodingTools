FROM python:3.11-slim

WORKDIR /app

# Copy project root
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r api/requirements.txt
RUN pip install --no-cache-dir -r bot/requirements.txt

ENV PORT=8000
ENV API_BASE_URL=http://127.0.0.1:8000

EXPOSE 8000

# Run API as primary process and keep bot in restart loop
CMD ["sh", "-c", "while true; do cd /app/bot && python3 bot.py; sleep 5; done & exec uvicorn api.main:app --host 0.0.0.0 --port $PORT"]
