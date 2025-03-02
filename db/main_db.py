import sqlite3

def setup_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          category TEXT,
                          size TEXT,
                          price REAL,
                          article TEXT UNIQUE,
                          photo TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          article TEXT,
                          size TEXT,
                          quantity INTEGER,
                          contact TEXT,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(article) REFERENCES products(article))''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_article ON orders(article)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_article ON products(article)")
        conn.commit()
