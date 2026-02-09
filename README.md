# VibeCoding Tools

🛠 База ресурсов для AI-кодинга с Telegram-ботом для автоматического добавления новых инструментов.

## Особенности

- 🤖 **Telegram-бот** - отправьте ссылку, бот автоматически:
  - Парсит страницу
  - Получает иконку и описание
  - Определяет категорию через AI
  - Добавляет в базу данных
- 📊 **JSON база данных** - простая структура, хранится в Git
- 🎨 **AI-классификация** - автоопределение категории по ключевым словам
- 🌐 **Веб-интерфейс** - красивая страница с категориями

## Структура проекта

```
VibeCodingTools/
├── data/
│   └── resources.json          # База данных ресурсов
├── api/
│   ├── main.py                  # FastAPI приложение
│   ├── Dockerfile               # Docker контейнер
│   └── requirements.txt        # Python зависимости
├── bot/
│   ├── bot.py                   # Telegram бот
│   ├── .env.example             # Пример переменных окружения
│   └── requirements.txt        # Python зависимости
├── index-new.html               # Новая версия интерфейса
├── index.html                   # Оригинальный интерфейс
├── vercel.json                  # Конфиг для Vercel
└── railway.toml                # Конфиг для Railway
```

## Категории

1. AI-модели и API
2. AI-редакторы и кодинг-агенты
3. Skills & MCP
4. Деплой и хостинг
5. Дизайн и UI-референсы
6. Документация и фреймворки
7. Утилиты и продуктивность

## Локальный запуск

### API (FastAPI)

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API будет доступен на `http://localhost:8000`

### Telegram бот

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
API_BASE_URL=http://localhost:8000
```

Запустите бота:
```bash
python bot.py
```

## Деплой

### Vercel (фронтенд)

1. Подключите репозиторий к Vercel
2. Настройте build settings в `vercel.json`
3. Деплой произойдет автоматически

### Railway (API + бот)

1. Создайте новый проект на Railway
2. Добавьте сервисы:
   - Docker сервис для API (используйте `api/Dockerfile`)
   - Добавьте переменные окружения:
     - `TELEGRAM_BOT_TOKEN`
     - `PORT=8000`
3. Деплой произойдет автоматически

## API Эндпоинты

### GET `/api/resources`
Получить все ресурсы

### POST `/api/classify`
Классифицировать ресурс по URL
```json
{
  "url": "https://example.com"
}
```

### POST `/api/resources`
Добавить новый ресурс
```json
{
  "url": "https://example.com",
  "name": "Example Tool",
  "description": "Описание",
  "category": "ai-models"
}
```

### GET `/api/health`
Проверка здоровья API

## Telegram бот команды

- `/start` - Начать работу
- `/help` - Справка
- `/list` - Список всех ресурсов

Отправьте любую ссылку для автоматического добавления!

## Как это работает

1. Пользователь отправляет ссылку в Telegram
2. Бот отправляет URL в API для классификации
3. API парсит страницу (title, description)
4. Определяет категорию по ключевым словам
5. Отправляет результат пользователю
6. Пользователь подтверждает или меняет категорию
7. Ресурс сохраняется в `data/resources.json`

## AI Классификация

Классификация использует ключевые слова для определения категории:

| Категория | Ключевые слова |
|-----------|----------------|
| AI-модели и API | AI, LLM, API, model, OpenAI, Claude, Gemini, GLM |
| AI-редакторы и кодинг-агенты | editor, IDE, cursor, coding, agent, bot, assistant |
| Skills & MCP | MCP, skill, Beads, context, agent |
| Деплой и хостинг | deploy, hosting, Vercel, Railway, Render, Supabase |
| Дизайн и UI-референсы | design, UI, Canva, Dribbble, Figma, interface |
| Документация и фреймворки | docs, React, Tailwind, framework, guide |
| Утилиты и продуктивность | tool, utility, productivity, screenshot, note |

## Конфигурация

### bot/.env
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
API_BASE_URL=https://your-railway-app.railway.app
AI_API_KEY=optional_ai_api_key
```

## TODO

- [ ] Интеграция с реальным AI API (OpenAI/GLM)
- [ ] Добавить редактирование ресурсов
- [ ] Удаление ресурсов
- [ ] Поиск по ресурсам
- [ ] Авто-обновление иконок
- [ ] Рейтинг ресурсов
- [ ] Комментирование ресурсов

## Лицензия

MIT
