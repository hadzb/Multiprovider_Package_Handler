import sqlite3

# This is a wrapper class around the orders module, interfaces with the database system.
class Order:
    def __init__(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = """CREATE TABLE IF NOT EXISTS orders(
                order_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER,
                package_id INTEGER,
                service_id TEXT,
                link TEXT,
                comments TEXT,
                quantity TEXT,
                rate TEXT,
                interval TEXT,
                order_status TEXT
            )"""
            cursor.execute(query)
            connection.commit()
    


    def add_order(self, user_id, package_id,service_id,link,comments,quantity,rate=1,interval=1, order_status="initiated"):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "INSERT INTO orders (user_id, package_id,service_id,link,comments,quantity,rate,interval, order_status) VALUES (?,?,?,?,?,?,?,?,?)"
            cursor.execute(query, (user_id, package_id,service_id,link,comments,quantity,rate,interval, order_status))
            connection.commit()
            return {"status": True, "message": f"Added order for user {user_id}"}
    

    def change_order_status(self,status,order_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            cursor.execute("UPDATE orders set order_status=? WHERE order_id=?",(status,order_id))
            connection.commit()

    def get_order(self, order_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM orders WHERE order_id=?"
            params = order_id
            cursor.execute(query, (params,))
            result = cursor.fetchone()
            return result
        
    def query_order_by_user(self,user_id):
            with sqlite3.connect("file.db") as connection:
                cursor = connection.cursor()
                query = "SELECT * FROM orders WHERE user_id=?"
                params = user_id
                cursor.execute(query, (params,))
                result = cursor.fetchall()

            collection=[]
            for i in result:
                data=dict()
                data["order_id"]=i[0]
                data["user_id"]=i[1]
                data["package_id"]=i[2]
                data["service_id"]=i[3]
                data["link"]=i[4]
                data["comments"]=i[5]
                data["quantity"]=i[6]
                data["rate"]=i[7]
                data["interval"]=i[8]
                data["order_status"]=i[9]
                collection.append(data)
            
            return collection

    def get_all_orders(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM orders"
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        
    def get_pending_orders(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM orders WHERE order_status=?"
            cursor.execute(query,('scheduled',))
            results = cursor.fetchall()
            return results


    def delete_order(self, order_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
            connection.commit()
            return {"status": True, "message": f"Successfully deleted order {order_id} from database"}
        
        
# with sqlite3.connect("file.db") as connection:
#     cursor=connection.cursor()
#     cursor.execute("DROP TABLE orders")
#     connection.commit()