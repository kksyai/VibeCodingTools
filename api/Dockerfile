FROM python:3.11-slim

WORKDIR /app

# Copy project root
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r api/requirements.txt
RUN pip install --no-cache-dir -r bot/requirements.txt

ENV PORT=8000
ENV API_BASE_URL=http://0.0.0.0:8000

EXPOSE 8000

# Run both API and bot
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT & cd /app/bot && python3 bot/bot.py"]