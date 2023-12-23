import sqlite3
import os

class ApiDatabase:
    def __init__(self,db_path=os.path.join(os.path.dirname(__file__),"file.db")):
        self.connection=sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor=self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys(
                user_id TEXT PRIMARY KEY,
                api_key TEXT,
                expiration_date TEXT
            )
        """)
        self.connection.commit()

    def close(self):
        self.connection.close()


