import sqlite3
#This is a wrapper class around the providers module, interfaces with the database system.
class Provider:
    def __init__(self):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query="""CREATE TABLE IF NOT EXISTS providers(
                provider_id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT,
                provider_url TEXT,
                provider_key TEXT
            )"""
            cursor.execute(query)
            connection.commit()
        

    def add_provider(self,name,url,key):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query="INSERT INTO providers (provider_name,provider_url,provider_key) VALUES (?,?,?)"
            cursor.execute(query,(name,url,key.strip()))

            connection.commit()
        
            return {"status":True,"message":f"Added {name} to the list of the providers"}

    def edit_provider(self,update_data):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query="UPDATE providers SET provider_name=?,provider_url=?,provider_key=? WHERE provider_id=?"
            params=update_data
            cursor.execute(query,params)
            connection.commit()
            return {"status":True,"message":f"Successfully updated provider {update_data[2]}"}

    def get_provider(self,provider_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query="SELECT * FROM providers WHERE provider_id=?"
            params=provider_id
            cursor.execute(query,(params,))
            result=cursor.fetchone()
            return result

    def get_all_providers(self):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            query="SELECT * FROM providers"
            cursor.execute(query)
            results=cursor.fetchall()

            return results

    def delete_provider(self,provider_id):
        with sqlite3.connect("file.db") as connection:
            cursor=connection.cursor()
            cursor.execute("DELETE FROM providers WHERE provider_id=?",(provider_id,))
            connection.commit()
            try:

                cursor.execute(f"DROP TABLE services_{provider_id}")
                connection.commit()
            except sqlite3.OperationalError as e:
                pass
            finally:

                return{"status":True,"message":f"Successfully deleted entry {provider_id} from database"}
        
