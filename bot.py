from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from download import *

BOT_TOKEN = "7744640850:AAHWd1JLfF61_fLe8nPeD-IUZaPvfUvr5Qk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я эхо-бот. Напиши что-нибудь, и я повторю!\nИспользуй /audio для получения музыки")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"Начинаем скачивание!")

    if os.path.exists():                               
        await context.bot.send_audio(
                chat_id=update.effective_chat.id,                           audio=open(AUDIO_PATH, 'rb'),
                title="Пример аудио",                                       performer="Мой бот"                                     )

# Новая функция для отправки аудио
async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:

        if os.path.exists(AUDIO_PATH):
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=open(AUDIO_PATH, 'rb'),
                title="Пример аудио",
                performer="Мой бот"
            )
        else:
            await update.message.reply_text("Аудиофайл не найден 😞")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", send_audio))  # Новая команда
    
    # Обработчик текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Обработчик ошибок
    app.add_error_handler(error)
    
    print("Бот запущен...")
    app.run_polling(poll_interval=3)
