import sqlite3

class ApiTable:
    def __init__(self, db_file='file.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS api_calls(
                    call_id INTEGER PRIMARY KEY,
                    packageId TEXT
                )
            ''')

    def add_call(self, call_id, package_id):
        with sqlite3.connect("file.db") as conn:
            cursor=conn.cursor()
            cursor.execute('''
                INSERT INTO api_calls (call_id, packageId)
                VALUES (?, ?)
            ''', (call_id, package_id))

            conn.commit()

    def get_call(self, call_id):
        with sqlite3.connect("file.db") as conn:
            cursor = conn.execute('''
                SELECT * FROM api_calls
                WHERE call_id = ?
            ''', (call_id,))
            return cursor.fetchone()

    def get_calls_by_package(self, package_id):
        with sqlite3.connect("file.db") as conn:
            cursor = conn.execute('''
                SELECT * FROM api_calls
                WHERE packageId = ?
            ''', (package_id,))
            return cursor.fetchall()

    def get_all(self):
        with sqlite3.connect("file.db") as conn:
            cursor=conn.execute("SELECT * FROM api_calls")
            all_records=cursor.fetchall()
            collection=[]

            for i in all_records:
                item=dict()
                item["call_id"]=i[0]
                item["package_id"]=i[1]
                collection.append(item)

        return collection

    def close_connection(self):
        self.conn.close()