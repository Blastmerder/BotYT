from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from download import *
import shutil
import re
import asyncio
import json

last = ""


def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Удаляет файл или ссылку
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Удаляет пустую папку
        except Exception as e:
            print(f'Не удалось удалить {file_path}. Причина: {e}')
clear_folder('./cash')

with open('token.json', 'r', encoding='UTF-8') as token:
    BOT_TOKEN = json.load(token)["token"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я эхо-бот. Напиши что-нибудь, и я повторю!\nИспользуй /audio для получения музыки")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text(f"Начинаем скачивание!")

    loop = asyncio.get_event_loop()
    mp3_file = await loop.run_in_executor(None, download_music, url)

    await update.message.reply_text(f"Отправляем файл")

    if os.path.exists(mp3_file):
        print("File found.")

        await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=open(mp3_file, 'rb'),
                read_timeout=180,
                write_timeout=180
            )


def download_music(url):
    data = get_data(url)

    title = re.sub(r'[\\/*?,:"<>|]', '', data['title'])
    title = re.sub(r'\s+', '_', title)
    mp3_file = f"./cash/{title}.mp3"
    last = mp3_file

    download_audio(url, "./cash/", title)
    thumbnail = get_thumbnail(data["thumbnail_url"])
    set_metadata(mp3_file, data["title"], data["author"], thumbnail)

    os.remove(thumbnail)

    return mp3_file 

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
