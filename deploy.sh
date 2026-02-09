#!/bin/bash

echo "VibeCoding Tools - Deploy"
echo "========================="
echo ""

if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI не установлен"
    echo "Установите: npm install -g vercel"
    exit 1
fi

cd "$(dirname "$0")"

echo "Деплой на Vercel..."
vercel --prod --yes
echo ""
echo "Vercel: Готово!"
echo ""
echo "Railway деплоится автоматически через git push."
echo ""
echo "Проверьте: https://vibecodingtools.vercel.app"
