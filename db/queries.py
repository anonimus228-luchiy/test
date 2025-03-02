import sqlite3
from config import STAFF, bot
import asyncio

def add_product(name, category, size, price, article, photo):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, size, price, article, photo) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, category, size, price, article, photo))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

async def notify_staff(order_details):
    for staff_id in STAFF:
        try:
            await bot.send_message(chat_id=int(staff_id), text=f"Новый заказ: {order_details}")
        except Exception as e:
            print(f"Ошибка отправки уведомления сотруднику {staff_id}: {e}")

def add_order(article, size, quantity, contact):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (article, size, quantity, contact) VALUES (?, ?, ?, ?)",
                   (article, size, quantity, contact))
    conn.commit()
    conn.close()

    order_details = f"Артикул: {article}, Размер: {size}, Количество: {quantity}, Контакт: {contact}"

    asyncio.create_task(notify_staff(order_details))  # Запускаем асинхронное уведомление сотрудников
