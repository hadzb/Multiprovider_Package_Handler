import sqlite3

class Package:
    def __init__(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = """CREATE TABLE IF NOT EXISTS packages(
                package_id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT,
                package_price REAL,
                package_provider TEXT
            )"""
            cursor.execute(query)
            connection.commit()
        print("Packages table is ready!")

    def add_package(self,name,price,rate,interval,provider):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "INSERT INTO packages (package_name,package_price,package_provider) VALUES (?, ?, ?)"
            cursor.execute(query, (name, price, provider))
            connection.commit()
            return {"status": True, "message": f"Added package {name} to the list of packages"}

    def edit_package(self, update_data):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "UPDATE packages SET package_name=?,package_price=?,package_provider=? WHERE package_id=?"
            params = update_data
            cursor.execute(query, params)
            connection.commit()
            return {"status": True, "message": f"Successfully updated package {update_data[0]}"}

    def get_package(self, package_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM packages WHERE package_id=?"
            params = package_id
            cursor.execute(query, (params,))
            result = cursor.fetchone()
            return result

    def get_all_packages_(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM packages"
            cursor.execute(query)
            results = cursor.fetchall()

            collection=[]
            for i in results:
                data=dict()
                data["package_id"]=i[0]
                data["package_name"]=i[1]
                collection.append(data)
            return collection
    
    def get_all_packages(self):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM packages"
            cursor.execute(query)
            results = cursor.fetchall()

        return results


    def delete_package(self, package_id):
        with sqlite3.connect("file.db") as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM packages WHERE package_id=?", (package_id,))
            connection.commit()
            return {"status": True, "message": f"Successfully deleted package {package_id} from database"}
        

# with sqlite3.connect("file.db") as connection:
#     cursor=connection.cursor()
#     cursor.execute("DROP TABLE packages")
#     connection.commit()