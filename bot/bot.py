import os
import re
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    welcome_text = """🛠 VibeCoding Tools Bot

Отправьте мне ссылку на ресурс, и я:
1. Парсирую страницу
2. Получу иконку и описание
3. Определю категорию через AI
4. Добавлю в базу данных

Поддерживаемые категории:
• AI-модели и API
• AI-редакторы и кодинг-агенты
• Skills & MCP
• Деплой и хостинг
• Дизайн и UI-референсы
• Документация и фреймворки
• Утилиты и продуктивность

Просто отправьте ссылку! 🚀"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """📖 Справка:

/start - Начать работу
/help - Эта справка
/list - Список всех ресурсов
/add - Добавить ресурс вручную

Отправьте любую ссылку для автоматического добавления!"""
    
    await update.message.reply_text(help_text)

async def list_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all resources"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/resources")
            
        if response.status_code == 200:
            data = response.json()
            total = sum(len(cat["tools"]) for cat in data["categories"].values())
            
            text = f"📚 Всего ресурсов: {total}\n\n"
            
            for cat_id, cat_data in data["categories"].items():
                text += f"🔹 {cat_data['name']}: {len(cat_data['tools'])}\n"
            
            await update.message.reply_text(text)
        else:
            await update.message.reply_text("❌ Не удалось загрузить список ресурсов")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL messages"""
    text = update.message.text
    
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        await update.message.reply_text("⚠️ Не найдено валидной ссылки. Пожалуйста, отправьте URL.")
        return
    
    url = urls[0]
    user_id = update.effective_user.id
    
    await update.message.reply_text(f"🔍 Обрабатываю: {url}\n\n⏳ Получаю информацию...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/classify",
                json={"url": url},
                timeout=30.0
            )
        
        if response.status_code == 200:
            result = response.json()
            
            pending_resources[user_id] = result
            
            keyboard = [
                [
                    InlineKeyboardButton(f"✅ Добавить в {categories_map.get(result['category'], result['category'])}", 
                                        callback_data=f"confirm_{user_id}"),
                    InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_{user_id}")
                ],
                [
                    InlineKeyboardButton("🔄 Другая категория", callback_data=f"change_{user_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            preview_text = f"""📦 Предварительный просмотр:

🔗 {result['url']}
📛 {result['name']}
📝 {result['description']}
🏷️ Категория: {categories_map.get(result['category'], result['category'])}

Подтвердите добавление:"""
            
            await update.message.reply_text(preview_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"❌ Не удалось обработать ссылку")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка обработки: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == f"confirm_{user_id}":
        resource = pending_resources.get(user_id)
        
        if not resource:
            await query.edit_message_text("⚠️ Ресурс не найден")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/resources",
                    json=resource
                )
            
            if response.status_code == 200:
                await query.edit_message_text(f"✅ Ресурс '{resource['name']}' успешно добавлен!")
                del pending_resources[user_id]
            else:
                await query.edit_message_text(f"❌ Ошибка добавления: {response.status_code}")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")
    
    elif query.data == f"cancel_{user_id}":
        if user_id in pending_resources:
            del pending_resources[user_id]
        await query.edit_message_text("❌ Добавление отменено")
    
    elif query.data == f"change_{user_id}":
        resource = pending_resources.get(user_id)
        
        if not resource:
            await query.edit_message_text("⚠️ Ресурс не найден")
            return
        
        keyboard = []
        for cat_id, cat_name in categories_map.items():
            keyboard.append([InlineKeyboardButton(cat_name, callback_data=f"cat_{cat_id}_{user_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏷️ Выберите категорию:", reply_markup=reply_markup)
    
    elif query.data.startswith(f"cat_"):
        parts = query.data.split("_")
        cat_id = parts[1]
        
        if user_id in pending_resources:
            pending_resources[user_id]['category'] = cat_id
            
            resource = pending_resources[user_id]
            
            keyboard = [
                [
                    InlineKeyboardButton(f"✅ Добавить в {categories_map.get(cat_id, cat_id)}", 
                                        callback_data=f"confirm_{user_id}"),
                    InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_{user_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            preview_text = f"""📦 Обновленный просмотр:

🔗 {resource['url']}
📛 {resource['name']}
📝 {resource['description']}
🏷️ Категория: {categories_map.get(cat_id, cat_id)}

Подтвердите добавление:"""
            
            await query.edit_message_text(preview_text, reply_markup=reply_markup)

def main() -> None:
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_resources))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    print("🤖 Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()