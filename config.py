from decouple import config
from aiogram import Bot

TOKEN = config("BOT_TOKEN")
STAFF = list(map(str, [7041912200]))  # Убрал лишнюю запятую

bot = Bot(token=TOKEN)  # Передаём токен
