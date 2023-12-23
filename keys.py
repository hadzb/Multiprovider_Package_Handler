import uuid
import datetime
import sqlite3
import database

class KeyGen:
    def __init__(self):
        self.database=database.ApiDatabase()
        

    def generate_key(self):
        user_id=str(uuid.uuid4())[:8]
        api_key=str(uuid.uuid4())
        expiration_date=datetime.datetime.utcnow()+datetime.timedelta(days=30)

        cusor=self.database.connection.cursor()
        cusor.execute("INSERT INTO api_keys (user_id,api_key,expiration_date) VALUES (?,?,?)",(user_id,api_key,expiration_date))
        self.database.connection.commit()

        print("Generated API keys.")

        self.database.close()
        return {"api_key":api_key,"expiry":str(expiration_date.date())}

    def validate_key(self,user_id,api_key):
        #check if the api key is in the database, if not raise and return an invalid key exception.
        cusor=self.database.connection.cursor()
        cusor.execute("""SELECT * FROM api_keys WHERE user_id=? AND api_key=?""",(user_id,api_key))
        result=cusor.fetchone() 
        if result:
            expiration_date=datetime.datetime.fromisoformat(result[2])
            if datetime.datetime.utcnow() < expiration_date:
                return {"validity":True, "message":"API key is valid"}
            else:
                return {"validity":False,"message":"API key has expired"}
        else:
            return {"validity":False,"message":"Invalid API Key"}
        

a=KeyGen()