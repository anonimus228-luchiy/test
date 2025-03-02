from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db.queries import add_product
from config import STAFF

class FSMProduct(StatesGroup):
    name = State()
    category = State()
    size = State()
    price = State()
    article = State()
    photo = State()

async def start_add_product(message: types.Message):
    if message.from_user.id not in STAFF:
        await message.answer("У вас нет прав на добавление товаров.")
        return
    await FSMProduct.name.set()
    await message.answer("Введите название товара:")

async def load_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await FSMProduct.next()
    await message.answer("Введите категорию товара:")

async def load_product_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await FSMProduct.next()
    await message.answer("Введите размер товара:")

async def load_product_size(message: types.Message, state: FSMContext):
    await state.update_data(size=message.text)
    await FSMProduct.next()
    await message.answer("Введите цену товара:")

async def load_product_price(message: types.Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("Пожалуйста, введите корректное число.")
        return
    await state.update_data(price=float(message.text))
    await FSMProduct.next()
    await message.answer("Введите артикул товара:")

async def load_product_article(message: types.Message, state: FSMContext):
    await state.update_data(article=message.text)
    await FSMProduct.next()
    await message.answer("Отправьте фото товара:")

async def load_product_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)

    add_product(data['name'], data['category'], data['size'], data['price'], data['article'], photo_id)
    await state.finish()
    await message.answer("Товар успешно добавлен!")

def register_product_handlers(dp: Dispatcher):
    dp.register_message_handler(start_add_product, commands="add_product", state=None)
    dp.register_message_handler(load_product_name, state=FSMProduct.name)
    dp.register_message_handler(load_product_category, state=FSMProduct.category)
    dp.register_message_handler(load_product_size, state=FSMProduct.size)
    dp.register_message_handler(load_product_price, state=FSMProduct.price)
    dp.register_message_handler(load_product_article, state=FSMProduct.article)
    dp.register_message_handler(load_product_photo, state=FSMProduct.photo, content_types=['photo'])
