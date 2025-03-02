from aiogram import executor
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.product import register_product_handlers
from handlers.order import register_order_handlers
from handlers.commands import register_common_handlers

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

register_common_handlers(dp)
register_product_handlers(dp)
register_order_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
