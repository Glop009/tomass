import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Токен бота не найден! Убедитесь, что переменная окружения TELEGRAM_TOKEN установлена.")

# Функция обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне ссылку на видео из YouTube, Instagram или TikTok, и я скачаю его для тебя без водяных знаков!"
    )

# Функция обработки сообщений с ссылками
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    # Проверяем, что сообщение содержит ссылку
    if "youtube.com" in user_message or "youtu.be" in user_message or "instagram.com" in user_message or "tiktok.com" in user_message:
        await update.message.reply_text("Скачиваю видео, подождите немного...")

        try:
            # Создаём папку для загрузок
            os.makedirs("downloads", exist_ok=True)

            # Указываем название выходного файла
            output_file = f"downloads/{chat_id}_video.mp4"

            # Используем yt-dlp для скачивания видео
            subprocess.run(
                ["yt-dlp", "-f", "best", user_message, "-o", output_file],
                check=True
            )

            # Отправляем скачанное видео пользователю
            await update.message.reply_video(video=open(output_file, "rb"))
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка при скачивании видео: {e}")
        finally:
            # Удаляем файл после отправки
            if os.path.exists(output_file):
                os.remove(output_file)
    else:
        await update.message.reply_text("Отправьте корректную ссылку на видео!")

# Основной блок программы
if __name__ == "__main__":
    # Создаём приложение
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))  # Команда /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))  # Обработка текстовых сообщений

    # Запуск бота
    print("Бот запущен...")
    app.run_polling()