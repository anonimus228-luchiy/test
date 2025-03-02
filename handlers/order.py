from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db.queries import add_order
from config import STAFF, bot

class FSMOrder(StatesGroup):
    article = State()
    size = State()
    quantity = State()
    contact = State()

async def start_order(message: types.Message):
    await FSMOrder.article.set()
    await message.answer("Введите артикул товара, который хотите купить:")

async def load_article(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    await FSMOrder.next()
    await message.answer("Введите размер товара:")

async def load_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await FSMOrder.next()
    await message.answer("Введите количество товара:")

async def load_quantity(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    await state.update_data(quantity=int(message.text))
    await FSMOrder.next()
    await message.answer("Введите ваш номер телефона для связи:")

async def load_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    contact = message.text
    await state.update_data(contact=contact)

    order_info = (
        f"Новый заказ:\n"
        f"Артикул: {data['article']}\n"
        f"Размер: {data['size']}\n"
        f"Количество: {data['quantity']}\n"
        f"Контакт: {contact}"
    )

    add_order(data["article"], data["size"], data["quantity"], contact)

    if not STAFF:
        await message.answer("Ошибка: Список сотрудников пуст. Проверьте config.py.")
        return

    for staff_id in STAFF:
        try:
            staff_id = int(staff_id)
            await bot.send_message(staff_id, order_info)
        except Exception as e:
            print(f"Ошибка отправки сообщения сотруднику {staff_id}: {e}")

    await state.finish()
    await message.answer("Ваш заказ успешно оформлен!")

def register_order_handlers(dp: Dispatcher):
    dp.register_message_handler(start_order, commands="order", state=None)
    dp.register_message_handler(load_article, state=FSMOrder.article)
    dp.register_message_handler(load_size, state=FSMOrder.size)
    dp.register_message_handler(load_quantity, state=FSMOrder.quantity)
    dp.register_message_handler(load_contact, state=FSMOrder.contact)
