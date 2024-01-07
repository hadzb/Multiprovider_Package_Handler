import sqlite3

class DisplayOrdersTable:
    def __init__(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = """CREATE TABLE IF NOT EXISTS display_orders(
                order_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER,
                package_id INTEGER,
                service_id TEXT,
                link TEXT,
                comments TEXT,
                quantity TEXT,
                rate TEXT,
                interval TEXT,
                call_id TEXT,
                order_status TEXT,
                execution_time TEXT
            )"""
            cursor.execute(query)
            connection.commit()

    def add_order(self, user_id, package_id,service_id,link,comments,call_id,quantity,rate=1,interval=1, order_status="initiated"):
        with sqlite3.connect("file.db") as connection:
            print(quantity,rate,interval)
            cursor = connection.cursor()
            query = "INSERT INTO orders (user_id, package_id,service_id,link,comments,quantity,rate,interval,call_id,order_status,execution_time) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
            cursor.execute(query, (user_id, package_id,service_id,link,comments,str(quantity),str(rate),str(interval),call_id, order_status))
            connection.commit()
            return {"status": True, "message": f"Added order for user {user_id}"}

    def change_order_status(self,status,order_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            cursor.execute("UPDATE display_orders set order_status=? WHERE order_id=?",(status,order_id))
            connection.commit()

    def get_order(self, order_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM display_orders WHERE order_id=?"
            params = order_id
            cursor.execute(query, (params,))
            result = cursor.fetchone()
            return result

    def get_pending_orders(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM display_orders WHERE order_status=?"
            cursor.execute(query,('scheduled',))
            results = cursor.fetchall()
            return results

    def delete_order(self, order_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM display_orders WHERE order_id=?", (order_id,))
            connection.commit()
            return {"status": True, "message": f"Successfully deleted order {order_id} from database"}