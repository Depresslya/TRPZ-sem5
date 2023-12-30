import sqlite3
from datetime import datetime
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                keywords TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    async def log_request(self, filename, keywords):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (timestamp, filename, keywords) 
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), filename, ','.join(keywords)))
        conn.commit()
        conn.close()