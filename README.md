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
│   └── resources.json           # База данных ресурсов
├── bot/
│   ├── bot.py                   # Telegram бот
│   ├── .env.example             # Пример переменных окружения
│   ├── requirements.txt         # Python зависимости
│   └── Dockerfile               # Docker контейнер
├── index.html                   # Веб-интерфейс
├── vercel.json                  # Конфиг для Vercel
└── railway.toml                 # Конфиг для Railway
 ```

## Деплой

📖 **Подробные инструкции**: см. [DEPLOYMENT.md](DEPLOYMENT.md)

### Быстрый старт:

1. **Vercel (фронтенд)**: https://vercel.com/new
2. **Railway (Telegram бот)**: https://railway.app/new

### После деплоя:

1. Проверьте фронтенд: `https://vibecodingtools.vercel.app`
2. Проверьте JSON-данные: `https://vibecodingtools.vercel.app/data/resources.json`
3. Протестируйте бота: `@kksyairenderbot`

## Категории

1. AI-модели и API
2. AI-редакторы и кодинг-агенты
3. Skills & MCP
4. Деплой и хостинг
5. Дизайн и UI-референсы
6. Документация и фреймворки
7. Утилиты и продуктивность

## Локальный запуск

### Telegram бот

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
GITHUB_TOKEN=your_github_personal_access_token
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

### Railway (Telegram бот)

1. Создайте новый проект на Railway
2. Добавьте Docker сервис (используйте `bot/Dockerfile`)
3. Добавьте переменные окружения:
   - `TELEGRAM_BOT_TOKEN`
   - `GITHUB_TOKEN`
4. Деплой произойдет автоматически

## Данные

### JSON база

Фронтенд читает данные из `data/resources.json`.

Проверьте актуальные данные:

`https://vibecodingtools.vercel.app/data/resources.json`

## Telegram бот команды

- `/start` - Начать работу
- `/help` - Справка
- `/list` - Список всех ресурсов

Отправьте любую ссылку для автоматического добавления!

## Как это работает

1. Пользователь отправляет ссылку в Telegram
2. Бот парсит страницу (title, description)
3. Определяет категорию по ключевым словам
4. Готовит превью и просит подтверждение пользователя
5. Пользователь подтверждает или меняет категорию
6. Ресурс сохраняется в `data/resources.json` через GitHub API

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
GITHUB_TOKEN=your_github_personal_access_token
```

## Безопасность секретов

- Локальные секреты храните только в `bot/.env` (файл уже в `.gitignore`)
- Runtime-логи (`logs/*.log`) не попадают в git
- Для проверки секретов перед коммитом используйте `gitleaks` через `pre-commit`:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
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
