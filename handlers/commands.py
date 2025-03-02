from aiogram import types, Dispatcher
from db.queries import get_products

async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот-магазин. Используйте /info для получения информации.")

async def cmd_info(message: types.Message):
    await message.answer("Этот бот предназначен для управления товарами и заказами.")

async def cmd_products(message: types.Message):
    products = get_products()
    if not products:
        await message.answer("Товаров пока нет.")
    else:
        text = "\n".join([f"{p[1]} - {p[4]} руб. (арт. {p[5]})" for p in products])
        await message.answer(text)

def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_info, commands="info")
    dp.register_message_handler(cmd_products, commands="products")
