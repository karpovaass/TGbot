import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext
import telegram.ext.filters as filters
from config import API_TOKEN, WEATHER_API_KEY, WEATHER_API_URL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Привет! Я бот для прогноза погоды. Используйте /weather для получения прогноза."
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "/start - Приветствие\n"
        "/help - Список команд\n"
        "/weather - Прогноз погоды"
    )

async def weather(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Введите название города:")
    return "GET_CITY"

def get_weather(city: str) -> str:
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(WEATHER_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather_desc = data['weather'][0]['description']
        temperature = main['temp']
        return f"Погода в {city}:\nТемпература: {temperature}°C\nОписание: {weather_desc.capitalize()}"
    else:
        logger.error(f"Ошибка API: {response.status_code} - {response.text}")
        return "Не удалось получить данные о погоде. Проверьте название города."

async def handle_message(update: Update, context: CallbackContext) -> None:
    city = update.message.text
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
