#!/bin/bash

echo "🚀 VibeCoding Tools - Setup Script"
echo ""

echo "📝 Creating .env files..."

# Bot .env
if [ ! -f "bot/.env" ]; then
    cp bot/.env.example bot/.env
    echo "✅ Created bot/.env"
    echo "⚠️  Please edit bot/.env and add your TELEGRAM_BOT_TOKEN"
else
    echo "ℹ️  bot/.env already exists"
fi

# Check if resources.json exists
if [ ! -f "data/resources.json" ]; then
    echo "❌ data/resources.json not found!"
    exit 1
else
    echo "✅ data/resources.json found"
fi

echo ""
echo "📋 Next steps:"
echo "1. Get Telegram bot token from @BotFather"
echo "2. Edit bot/.env and add TELEGRAM_BOT_TOKEN"
echo "3. Start API: cd api && uvicorn main:app --reload"
echo "4. Start bot: cd bot && python bot.py"
echo ""
echo "Or deploy to:"
echo "  - Vercel: https://vercel.com"
echo "  - Railway: https://railway.app"
echo ""