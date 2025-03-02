from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db.queries import add_product, get_products, add_order
from config import STAFF, bot

class FSMProduct(StatesGroup):
    name = State()
    category = State()
    size = State()
    price = State()
    article = State()
    photo = State()

async def start_add_product(message: types.Message):
    if str(message.from_user.id) not in STAFF:
        await message.answer("У вас нет прав на добавление товаров.")
        return
    await FSMProduct.name.set()
    await message.answer("Введите название товара:")

async def load_product_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMProduct.next()
    await message.answer("Введите категорию товара:")

async def load_product_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text
    await FSMProduct.next()
    await message.answer("Введите размер товара:")

async def load_product_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = message.text
    await FSMProduct.next()
    await message.answer("Введите цену товара:")

async def load_product_price(message: types.Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("Пожалуйста, введите корректное число.")
        return
    async with state.proxy() as data:
        data['price'] = float(message.text)
    await FSMProduct.next()
    await message.answer("Введите артикул товара:")

async def load_product_article(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['article'] = message.text
    await FSMProduct.next()
    await message.answer("Отправьте фото товара:")

async def load_product_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
        add_product(data['name'], data['category'], data['size'], data['price'], data['article'], data['photo'])
    await state.finish()
    await message.answer("Товар успешно добавлен!")

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

class FSMOrder(StatesGroup):
    article = State()
    size = State()
    quantity = State()
    contact = State()

async def start_order(message: types.Message):
    await FSMOrder.article.set()
    await message.answer("Введите артикул товара, который хотите купить:")

async def load_article(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['article'] = message.text
    await FSMOrder.next()
    await message.answer("Введите размер товара:")

async def load_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = message.text
    await FSMOrder.next()
    await message.answer("Введите количество товара:")

async def load_quantity(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите числовое значение.")
        return
    async with state.proxy() as data:
        data['quantity'] = int(message.text)
    await FSMOrder.next()
    await message.answer("Введите ваш номер телефона для связи:")

async def load_contact(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact'] = message.text

        print("📌 Данные перед отправкой уведомления:", data)  # Логируем данные

        add_order(data['article'], data['size'], data['quantity'], data['contact'])

        order_info = (f"Новый заказ:\n"
                      f"Артикул: {data.get('article', '❌ Нет данных')}\n"
                      f"Размер: {data.get('size', '❌ Нет данных')}\n"
                      f"Количество: {data.get('quantity', '❌ Нет данных')}\n"
                      f"Контакт: {data.get('contact', '❌ Нет данных')}")

        print("🔹 Отправляем уведомление сотрудникам:", order_info)  # Проверяем сообщение

    if not STAFF:
        print("❌ Ошибка: STAFF пуст. Проверь config.py")
        await message.answer("Ошибка отправки уведомления сотрудникам.")
        return

    for staff_id in STAFF:
        try:
            staff_id = str(staff_id).strip()  # Приводим ID к строке
            if staff_id.isdigit():  # Проверяем, что это ID
                await bot.send_message(chat_id=int(staff_id), text=order_info)
            else:
                print(f"⚠️ Пропущен некорректный ID: {staff_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения сотруднику {staff_id}: {e}")

    await state.finish()
    await message.answer("Ваш заказ успешно оформлен!")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_info, commands="info")
    dp.register_message_handler(cmd_products, commands="products")
    dp.register_message_handler(start_order, commands="order", state=None)
    dp.register_message_handler(load_article, state=FSMOrder.article)
    dp.register_message_handler(load_size, state=FSMOrder.size)
    dp.register_message_handler(load_quantity, state=FSMOrder.quantity)
    dp.register_message_handler(load_contact, state=FSMOrder.contact)
    dp.register_message_handler(start_add_product, commands="add_product", state=None)
    dp.register_message_handler(load_product_name, state=FSMProduct.name)
    dp.register_message_handler(load_product_category, state=FSMProduct.category)
    dp.register_message_handler(load_product_size, state=FSMProduct.size)
    dp.register_message_handler(load_product_price, state=FSMProduct.price)
    dp.register_message_handler(load_product_article, state=FSMProduct.article)
    dp.register_message_handler(load_product_photo, state=FSMProduct.photo, content_types=['photo'])
