import aiosqlite

DB_PATH = "my_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Создаем все таблицы сразу
        await db.execute('''
            CREATE TABLE IF NOT EXISTS authorized_users (
                user_id INTEGER PRIMARY KEY,
                name TEXT
            )''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                file_id TEXT
            )''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                amount INT
            )''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS wishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id BIGINT, 
                text TEXT
            )''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS important_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                info TEXT
            )''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                remind_at TIMESTAMP
            )''')
        await db.commit()

async def is_user_authorized(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM authorized_users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None

# Универсальная функция для записи (чтобы не дублировать код в хендлерах)
async def execute_query(query, params=()):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, params)
        await db.commit()

# Функция для получения данных
async def fetch_one(query, params=()):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            return await cursor.fetchone()

async def fetch_all(query, params=()):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def fetch_val(query, params=()):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0