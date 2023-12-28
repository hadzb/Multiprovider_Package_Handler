import sqlite3

with sqlite3.connect("file.db") as connection:
    cursor = connection.cursor()
    query = f"SELECT * FROM api_keys"
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

    print(results)