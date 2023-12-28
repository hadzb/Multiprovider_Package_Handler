import sqlite3
from provider_wrapper import ProviderWrapper

# This is a wrapper class around the services module, interfaces with the database system.
class Service:
    def __init__(self,provider_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            self.provider_id=provider_id
            query = f"""CREATE TABLE IF NOT EXISTS services_{provider_id}(
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cancel TEXT,
                category TEXT,
                dripfeed TEXT,
                max TEXT,
                min TEXT,
                name TEXT,
                refill TEXT,
                service TEXT,
                type TEXT,
                rate INTEGER,
                interval INTEGER
            )"""
            cursor.execute(query)
            connection.commit()

    def add_service(self,data):
        if type(data)==tuple:
            with sqlite3.connect("file.db") as connection:
                cursor = connection.cursor()
                query = f"INSERT INTO services_{self.provider_id} (cancel,category,dripfeed,max,min,name,refill,service,type,rate,interval) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                cursor.execute(query,data)
                connection.commit()
                return {"status": True, "message": f"Added service {data[5]} to the list of services_{self.provider_id}"}

        elif type(data)==list:
            with sqlite3.connect("file.db") as connection:
                cursor = connection.cursor()
                query = f"INSERT INTO services_{self.provider_id} (cancel,category,dripfeed,max,min,name,refill,service,type,rate,interval) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                cursor.executemany(query,data)
                connection.commit()
                return {"status": True, "message": f"Added service to the list of services_{self.provider_id}"}
    
        
    def initialize_services(self):
        provider=ProviderWrapper(self.provider_id)
        services=provider.get_all_services()
        all_serv=[]
        print(services)
        for s in services:
            n_services=(s.get("cancel"),s.get("category"),s.get("dripfeed"),s.get("max"),s.get("min"),s.get("name"),s.get("refill"),s.get("service"),s.get("type"),1,1)
            all_serv.append(n_services)

        self.add_service(all_serv)


    def edit_service(self, update_data):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = f"UPDATE services_{self.provider_id} SET rate=?, interval=? WHERE service_id=?"
            params = update_data
            cursor.execute(query, params)
            connection.commit()
            return {"status": True, "message": f"Successfully updated service {update_data[0]}"}

    def get_service(self, service_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM services_{self.provider_id} WHERE service_id=?"
            params = service_id
            cursor.execute(query, (params,))
            result = cursor.fetchone()
            return result
        
    def get_jap_service(self,jap_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query=f"SELECT * FROM services_{self.provider_id} WHERE service=?"
            params=jap_id
            cursor.execute(query,(params,))
            result=cursor.fetchone()
            return result

    def get_all_services(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM services_{self.provider_id}"
            cursor.execute(query)
            results = cursor.fetchall()
            collection=[]
            for service in results:
                dict={}
                dict["service_id"]=service[0]
                dict["cancel"]=service[1]
                dict["category"]=service[2]
                dict["dripfeed"]=service[3]
                dict["max"]=service[4]
                dict["min"]=service[5]
                dict["name"]=service[6]                
                dict["refill"]=service[7]
                dict["service"]=service[8]
                dict["type"]=service[9]
                dict["rate"]=service[10]
                dict["interval"]=service[11]
                collection.append(dict)
                
            return collection


    def delete_service(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS service_{self.provider_id}")
            connection.commit()
            return {"status": True, "message": f"Successfully deleted table service_{self.provider_id} from database"}


    def parse_services(self,services):
        collection=[]
        for service in services:
            data=(service.get("cancel"),service.get("category"),service.get("dripfeed"),service.get("max"),service.get("min"),service.get("name"),service.get("refill"),service.get("type"),0,0)
            return data
        