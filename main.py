# main.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, STAFF
from db.queries import get_products, add_order

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderFSM(StatesGroup):
    article = State()
    size = State()
    quantity = State()
    contact = State()

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для управления товарами.")

@dp.message_handler(commands=["info"])
async def send_info(message: types.Message):
    await message.reply("Этот бот помогает управлять товарами и заказами.")

@dp.message_handler(commands=["products"])
async def list_products(message: types.Message):
    products = get_products()
    response = "Список товаров:\n" + "\n".join([f"{p[1]} - {p[4]}₽" for p in products])
    await message.reply(response)

@dp.message_handler(commands=["order"])
async def start_order(message: types.Message):
    await message.reply("Введите артикул товара:")
    await OrderFSM.article.set()

@dp.message_handler(state=OrderFSM.article)
async def order_article(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    await message.reply("Введите размер:")
    await OrderFSM.next()

@dp.message_handler(state=OrderFSM.size)
async def order_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.reply("Введите количество:")
    await OrderFSM.next()

@dp.message_handler(state=OrderFSM.quantity)
async def order_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.reply("Введите ваш номер телефона:")
    await OrderFSM.next()

@dp.message_handler(state=OrderFSM.contact)
async def order_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_order(data["article"], data["size"], data["quantity"], message.text)
    await message.reply("Ваш заказ оформлен!")
    await state.finish()

async def notify_staff(order_details):
    for staff_id in STAFF:
        await bot.send_message(staff_id, f"Новый заказ: {order_details}")

if __name__ == "__main__":
    from db.main_db import setup_db
    setup_db()
    executor.start_polling(dp, skip_updates=True)

