import sqlite3
from itertools import groupby
from datetime import datetime, timedelta
import time
from displayOrders import DisplayOrdersTable
from provider import Provider
class DiplayOrder:
    def __init__(self,order_id,user_id,package_id,service_id,link,comments,quantity,rate,interval,call_id,order_status,execution_time,jap_order_id,start,provider_name):
        self.order_id=order_id
        self.user_id=user_id
        self.package_id=package_id
        self.service_id=service_id
        self.link=link
        self.comments=comments
        self.quantity=quantity
        self.rate=rate
        self.interval=interval
        self.call_id=call_id
        self.order_status=order_status
        self.execution_time=execution_time
        self.jap_order_id=jap_order_id
        self.provider_name=provider_name
        self.order_start=start

        

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
                call_id TEXT,
                order_status TEXT,
                jap_order_id TEXT
            )"""
            cursor.execute(query)
            connection.commit()
    
    def add_order(self, user_id, package_id,service_id,link,comments,call_id,quantity,rate=1,interval=1, order_status="initiated"):
        with sqlite3.connect("file.db") as connection:
            print(quantity,rate,interval)
            cursor = connection.cursor()
            query = "INSERT INTO orders (user_id, package_id,service_id,link,comments,quantity,rate,interval,call_id,order_status) VALUES (?,?,?,?,?,?,?,?,?,?)"
            cursor.execute(query, (user_id, package_id,service_id,link,comments,str(quantity),str(rate),str(interval),call_id, order_status))
            connection.commit()

            return {"status": True, "message": f"Added order for user {user_id}"}
    
    def change_order_status(self,status,order_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            cursor.execute("UPDATE orders set order_status=? WHERE order_id=?",(status,order_id))
            connection.commit()

    def set_jap_order_id(self,jap_id,order_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            cursor.execute("UPDATE orders set jap_order_id=? WHERE order_id=?",(jap_id,order_id))
            connection.commit()

    def get_order(self, order_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM orders WHERE order_id=?"
            params = order_id
            cursor.execute(query, (params,))
            result = cursor.fetchone()
            return result
    
    def display_schedules(self,call_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query="SELECT * FROM orders WHERE call_id=?"
            params=(call_id,)
            cursor.execute(query,params)

            result=cursor.fetchall()

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
                data["call_id"]=i[9]
                data["order_status"]=i[10]
                collection.append(data)
                
            duplicated_orders=[]

            cumulative_execution_time = data["call_id"]

            for index,order in enumerate(collection):

                startTime=int(call_id)
                dt_starttime=datetime.utcfromtimestamp(startTime)
                start=dt_starttime.strftime('%Y-%m-%d %H:%M:%S UTC')
                
                cumulative_execution_time = int(order["call_id"])
                  
                cumulative_execution_time=cumulative_execution_time+int(order["interval"])
                dt_object = datetime.utcfromtimestamp(cumulative_execution_time)

                formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S UTC')

                provider_table=Provider()
                provider_name=provider_table.get_provider(data["package_id"])
                provider_name=provider_name[1]

                entry=DiplayOrder(order["order_id"],order["user_id"],order["package_id"],order["service_id"],order["link"],order["comments"],order["quantity"],order["rate"],order["interval"],order["call_id"],order["order_status"],formatted_time,"_",start,provider_name)
                print(f"Added Provider Name {entry.provider_name}")
                duplicated_orders.append(entry)
                
            return duplicated_orders

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
                data["call_id"]=i[9]
                data["order_status"]=i[10]
                collection.append(data)
            
            return collection

    def query_order_by_call(self,call_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM orders WHERE call_id=?"
            params = call_id
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
                data["call_id"]=i[9]
                data["order_status"]=i[10]
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

    def group_orders_by_calls(self):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            cursor.execute("SELECT * FROM orders")
            all_orders=cursor.fetchall()

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
                data["call_id"]=i[9]
                data["order_status"]=i[10]
                collection.append(data)

            return collection

    def query_orders_by_call(self,call_id):
            with sqlite3.connect("file.db") as connection:
                cursor=connection.cursor()
                cursor.execute("SELECT * FROM orders")
                all_orders=cursor.fetchall()

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
                    data["call_id"]=i[9]
                    data["order_status"]=i[10]
                    collection.append(data)

                collection.sort(key=lambda x: x['call_id'])
                grouped_collection = {key: list(group) for key, group in groupby(collection, key=lambda x: x['call_id'])}

            return grouped_collection[call_id]