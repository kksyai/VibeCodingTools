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
curl https://vibecodingtools.vercel.app/data/resources.json
```

---

## Railway (Telegram бот)

### Шаги:

1. **Откройте** https://railway.app/new
2. **Войдите** через GitHub
3. **Нажмите** "Deploy from GitHub repo"
4. **Выберите** репозиторий: `kksyai/VibeCodingTools`
5. **Настройте сервис:**
   - Select Service: `Docker` (использует `bot/Dockerfile`)
   - Environment Variables:
     ```
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     GITHUB_TOKEN=your_github_personal_access_token
     ```
6. **Нажмите** "Deploy"
7. **После деплоя** получите URL вида: `https://your-app.railway.app`

### Проверка:

```bash
curl https://vibecodingtools.vercel.app/data/resources.json
```

---

## После деплоя

### 1. Проверьте фронтенд

Откройте: `https://vibecodingtools.vercel.app`

### 2. Проверьте JSON-данные

```bash
curl https://vibecodingtools.vercel.app/data/resources.json
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

**Проблема:** Бот не запускается
- Проверьте логи в Railway dashboard
- Убедитесь что `TELEGRAM_BOT_TOKEN` и `GITHUB_TOKEN` заданы

**Проблема:** Бот не отвечает
- Проверьте что `TELEGRAM_BOT_TOKEN` задан правильно
- Убедитесь что Railway URL доступен
- Проверьте webhook или polling конфигурацию

---

## Локальный запуск

### Telegram бот:

```bash
cd bot
pip install -r requirements.txt
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

- `TELEGRAM_BOT_TOKEN=...` - токен Telegram бота
- `GITHUB_TOKEN=...` - GitHub token с правами на запись в repo

### Local (.env):

```bash
TELEGRAM_BOT_TOKEN=...
GITHUB_TOKEN=...
```

---

## Структура проекта

```
VibeCodingTools/
├── index.html              # Фронтенд
├── data/
│   └── resources.json      # База данных ресурсов
├── bot/
│   ├── bot.py            # Telegram бот
│   ├── .env              # Переменные окружения
│   └── requirements.txt   # Python зависимости
├── vercel.json           # Конфиг для Vercel
├── railway.toml          # Конфиг для Railway
└── .gitignore           # Исключения для git
```

---

## Связь

GitHub: https://github.com/kksyai/VibeCodingTools
Telegram: @kksyairenderbot
