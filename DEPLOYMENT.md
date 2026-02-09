# 🚀 Инструкции по деплою

## Vercel (Фронтенд)

### Шаги:

1. **Откройте** https://vercel.com/new
2. **Войдите** через GitHub
3. **Нажмите** "Continue with GitHub"
4. **Выберите** репозиторий: `kksyai/VibeCodingTools`
5. **Настройки:**
   - Framework Preset: `Other`
   - Root Directory: `/`
   - Build Command: (оставьте пустым)
   - Output Directory: `/`
6. **Нажмите** "Deploy"
7. **Через минуту** получите URL вида: `https://vibecodingtools.vercel.app`

### Проверка:

```bash
curl https://vibecodingtools.vercel.app/api/health
```

---

## Railway (API + Telegram бот)

### Шаги:

1. **Откройте** https://railway.app/new
2. **Войдите** через GitHub
3. **Нажмите** "Deploy from GitHub repo"
4. **Выберите** репозиторий: `kksyai/VibeCodingTools`
5. **Настройте сервис:**
   - Select Service: `Docker` (использует `api/Dockerfile`)
   - Environment Variables:
     ```
     PORT=8000
     ZAI_API_KEY=e763f348ffec4dd1becf2fb52e0d3551.hWHmFvtWETiGQRSy
     TELEGRAM_BOT_TOKEN=8153467338:AAHfhbPRS9bM-EULuj4ubXLyL5mouGXJ0jo
     ```
6. **Нажмите** "Deploy"
7. **После деплоя** получите URL вида: `https://your-app.railway.app`

### Проверка:

```bash
curl https://your-app.railway.app/api/health
```

---

## После деплоя

### 1. Проверьте фронтенд

Откройте: `https://vibecodingtools.vercel.app`

### 2. Проверьте API

```bash
curl https://your-app.railway.app/api/health
curl https://your-app.railway.app/api/resources
```

### 3. Протестируйте бота

- Найдите в Telegram: `@kksyairenderbot`
- Отправьте: `/start`
- Отправьте ссылку, например: `https://github.com/vercel/next.js`

---

## Troubleshooting

### Vercel

**Проблема:** Не загружаются данные
- Проверьте что `data/resources.json` включен в деплой
- Проверьте консоль браузера (F12) на ошибки

**Проблема:** 404 ошибка
- Убедитесь что `index.html` существует в корне
- Проверьте настройки `vercel.json`

### Railway

**Проблема:** API не запускается
- Проверьте логи в Railway dashboard
- Убедитесь что порт 8000 указан в env переменных

**Проблема:** Бот не отвечает
- Проверьте что `TELEGRAM_BOT_TOKEN` задан правильно
- Убедитесь что Railway URL доступен
- Проверьте webhook или polling конфигурацию

---

## Локальный запуск

### API:

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Telegram бот:

```bash
cd bot
cp .env.example .env
# Отредактируйте .env
python bot.py
```

### Фронтенд:

```bash
python3 -m http.server 8080
# Откройте http://localhost:8080
```

---

## Переменные окружения

### Railway:

- `PORT=8000` - порт для API
- `ZAI_API_KEY=...` - API ключ для классификации
- `TELEGRAM_BOT_TOKEN=...` - токен Telegram бота

### Local (.env):

```bash
API_BASE_URL=http://localhost:8001
```

---

## Структура проекта

```
VibeCodingTools/
├── index.html              # Фронтенд
├── data/
│   └── resources.json      # База данных ресурсов
├── api/
│   ├── main.py            # FastAPI приложение
│   ├── Dockerfile         # Docker контейнер
│   └── requirements.txt   # Python зависимости
├── bot/
│   ├── bot.py            # Telegram бот
│   ├── .env             # Переменные окружения
│   └── requirements.txt   # Python зависимости
├── vercel.json           # Конфиг для Vercel
├── railway.toml          # Конфиг для Railway
└── .gitignore           # Исключения для git
```

---

## Связь

GitHub: https://github.com/kksyai/VibeCodingTools
Telegram: @kksyairenderbot