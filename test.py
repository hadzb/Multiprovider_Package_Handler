import sqlite3

with sqlite3.connect("file.db") as connection:
    cursor=connection.cursor()
    cursor.execute("DROP TABLE api_keys")
    connection.commit()
    