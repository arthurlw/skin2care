import sqlite3

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT CHECK(status IN ('pending', 'completed')) DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
