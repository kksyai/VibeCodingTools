import os
import re
import json
import base64
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from bot.core import append_resource_with_retry, classify_resource, validate_required_env

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "kksyai/VibeCodingTools"
DATA_PATH = "data/resources.json"

GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_PATH}"

categories_map = {
    "ai-models": "AI-модели и API",
    "ai-editors": "AI-редакторы и кодинг-агенты",
    "skills-mcp": "Skills & MCP",
    "deploy": "Деплой и хостинг",
    "design": "Дизайн и UI-референсы",
    "docs": "Документация и фреймворки",
    "utils": "Утилиты и продуктивность"
}

pending_resources = {}


# --- Utility functions (moved from api/main.py) ---

async def fetch_url_info(url: str) -> Optional[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, follow_redirects=True)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            title = None
            if soup.title and soup.title.string:
                title = soup.title.string.strip()

            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')

            return {
                "title": title,
                "description": description,
                "domain": url.split('/')[2]
            }
    except Exception as e:
        print(f"Error fetching {url}: {e}")

    return None


def get_favicon_url(domain: str) -> str:
    return f"https://www.google.com/s2/favicons?sz=64&domain={domain}"


def truncate_description(text: str, limit: int = 100) -> str:
    if not text:
        return text
    return text[:limit - 3] + "..." if len(text) > limit else text


# --- GitHub API helpers ---

def _github_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def github_read_resources() -> tuple[dict, str]:
    """Read resources.json from GitHub. Returns (data_dict, sha)."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(GITHUB_API, headers=_github_headers())
        resp.raise_for_status()
        payload = resp.json()
        content = base64.b64decode(payload["content"]).decode("utf-8")
        return json.loads(content), payload["sha"]


async def github_write_resources(data: dict, sha: str, message: str) -> None:
    """Write updated resources.json to GitHub."""
    data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    content_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    body = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("ascii"),
        "sha": sha,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.put(GITHUB_API, headers=_github_headers(), json=body)
        resp.raise_for_status()


# --- Bot handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = """VibeCoding Tools Bot

Отправьте мне ссылку на ресурс, и я:
1. Парсирую страницу
2. Получу иконку и описание
3. Определю категорию
4. Добавлю в базу на GitHub

Поддерживаемые категории:
- AI-модели и API
- AI-редакторы и кодинг-агенты
- Skills & MCP
- Деплой и хостинг
- Дизайн и UI-референсы
- Документация и фреймворки
- Утилиты и продуктивность

Просто отправьте ссылку!"""

    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """Справка:

/start - Начать работу
/help - Эта справка
/list - Список всех ресурсов

Отправьте любую ссылку для автоматического добавления!"""

    await update.message.reply_text(help_text)


async def list_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data, _ = await github_read_resources()
        total = sum(len(cat["tools"]) for cat in data["categories"].values())

        text = f"Всего ресурсов: {total}\n\n"
        for cat_data in data["categories"].values():
            text += f"- {cat_data['name']}: {len(cat_data['tools'])}\n"

        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)

    if not urls:
        await update.message.reply_text("Не найдено валидной ссылки. Пожалуйста, отправьте URL.")
        return

    url = urls[0]
    user_id = update.effective_user.id

    await update.message.reply_text(f"Обрабатываю: {url}\n\nПолучаю информацию...")

    try:
        url_info = await fetch_url_info(url)

        if url_info:
            name = url_info.get("title") or ""
            description = url_info.get("description") or ""
            domain = url_info.get("domain", "")
            icon = get_favicon_url(domain)
        else:
            name = ""
            description = ""
            parts = url.split('/')
            domain = parts[2] if len(parts) > 2 else ""
            icon = get_favicon_url(domain)

        if not name:
            name = domain.replace('www.', '').split('.')[0].capitalize()

        if not description:
            description = "Ресурс для разработки"

        description = truncate_description(description)
        category = classify_resource(url, name, description)

        result = {
            "url": url,
            "name": name,
            "description": description,
            "icon": icon,
            "category": category,
        }

        pending_resources[user_id] = result

        keyboard = [
            [
                InlineKeyboardButton(
                    f"Добавить в {categories_map.get(category, category)}",
                    callback_data=f"confirm_{user_id}"),
                InlineKeyboardButton("Отмена", callback_data=f"cancel_{user_id}")
            ],
            [
                InlineKeyboardButton("Другая категория", callback_data=f"change_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        preview_text = f"""Предварительный просмотр:

{result['url']}
Название: {result['name']}
Описание: {result['description']}
Категория: {categories_map.get(result['category'], result['category'])}

Подтвердите добавление:"""

        await update.message.reply_text(preview_text, reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"Ошибка обработки: {e}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == f"confirm_{user_id}":
        resource = pending_resources.get(user_id)

        if not resource:
            await query.edit_message_text("Ресурс не найден")
            return

        try:
            status = await append_resource_with_retry(
                resource,
                read_fn=github_read_resources,
                write_fn=github_write_resources,
                max_retries=2,
            )

            if status == "exists":
                await query.edit_message_text("Ресурс с таким ID уже существует")
                return

            await query.edit_message_text(f"Ресурс '{resource['name']}' добавлен! Сайт обновится через ~10 сек.")
            del pending_resources[user_id]

        except Exception as e:
            await query.edit_message_text(f"Ошибка: {e}")

    elif query.data == f"cancel_{user_id}":
        pending_resources.pop(user_id, None)
        await query.edit_message_text("Добавление отменено")

    elif query.data == f"change_{user_id}":
        resource = pending_resources.get(user_id)
        if not resource:
            await query.edit_message_text("Ресурс не найден")
            return

        keyboard = []
        for cat_id, cat_name in categories_map.items():
            keyboard.append([InlineKeyboardButton(cat_name, callback_data=f"cat_{cat_id}_{user_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите категорию:", reply_markup=reply_markup)

    elif query.data.startswith("cat_"):
        parts = query.data.split("_")
        cat_id = parts[1]

        if user_id in pending_resources:
            pending_resources[user_id]['category'] = cat_id
            resource = pending_resources[user_id]

            keyboard = [
                [
                    InlineKeyboardButton(
                        f"Добавить в {categories_map.get(cat_id, cat_id)}",
                        callback_data=f"confirm_{user_id}"),
                    InlineKeyboardButton("Отмена", callback_data=f"cancel_{user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            preview_text = f"""Обновленный просмотр:

{resource['url']}
Название: {resource['name']}
Описание: {resource['description']}
Категория: {categories_map.get(cat_id, cat_id)}

Подтвердите добавление:"""

            await query.edit_message_text(preview_text, reply_markup=reply_markup)


def main() -> None:
    validate_required_env(os.environ)
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_resources))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("Bot started")
    application.run_polling()


if __name__ == "__main__":
    main()
