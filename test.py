import sqlite3

with sqlite3.connect("file.db") as conn:
    cursor=conn.execute("SELECT * FROM api_calls")
    all_records=cursor.fetchall()
    collection=[]

    for i in all_records:
        item=dict()
        item["call_id"]=i[0]
        item["package_id"]=i[1]
        collection.append(item)

    print(collection[0]["call_id"])