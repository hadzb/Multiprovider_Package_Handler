from flask import Blueprint,render_template,request,redirect,url_for,jsonify
import sqlite3
from api import Api
import datetime
from packages import Package
from orders import Order
api_blueprint=Blueprint("api_blueprint",__name__)
my_api=Api("7627ead53418739cbdf69bd5fef497b0")
package_db=Package()


@api_blueprint.route("/order",methods=["POST"])
def add_order():
    if request.method=="POST":
        data=request.get_json()
        # begin by validating the api key
        key=data.get("key",None)
        user_id=data.get("user_id",None)
        if key==None or user_id==None:
            return {"error":"Bad Request"}

        results=validate_key(user_id,key)
        if results.get("validity",False):
            post_data=request.get_json()
            order_table=Order()
            user_id=post_data.get("user_id")
            package_id=post_data.get("service")

            #get the package from the database.
            p=Package()
            package=p.get_package(package_id)
            if(package==None):
                return {"error":"Invalid Service Id"}
            
            providers=package[4].split("|")
            link=post_data.get("link","")
            comments=post_data.get("comments",None)
            quantity=post_data.get("quantity",10)
            rate=""
            interval=""
            order_table=Order()
            for task in providers:
                package_id=task.split(":")[0]
                service_id=task.split(":")[1]
                prov_quantity=task.split(":")[2]
                order_status="initiated"
                user_id=post_data.get("user_id")
                if int(prov_quantity)<int(quantity):
                    quantity=prov_quantity
                print(user_id,package_id,service_id,link,comments,quantity,rate,interval,order_status)
                order_table.add_order(user_id,package_id,service_id,link,comments,quantity,rate,interval,order_status)
            return {"status":"sucesss","message":"Order was placed, check dashboard for progress"}
        else:
            return {"status":"failed","message":"Your account balance is insufficient"}
        

def validate_key(user_id,api_key):
    with sqlite3.connect("file.db") as connection:
        cusor=connection.cursor()
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

def handle_packages(order_name,link,quantity,comments):
    order_ids=order_name.split("+")
    res_arr=[]
    for order_id in order_ids:
        response=dict()
        order_id=int(order_id)
        print(order_id)
        if order_id==2929:
            response=my_api.order({"link":link,"quantity":quantity,"action":"add","quantity":quantity,"service":2929})
            res_arr.append(response)
        elif order_id==8187:
            response=my_api.order({"link":link,"comments":comments,"quantity":quantity,"action":"add","service":8187})
            res_arr.append(response)
        else:
            return {"error":"Service Id not Set for Packages : Contact Admin"}
    return res_arr


@api_blueprint.route("/status",methods=["POST"])
def get_status():
    if request.method=="POST":
        id=request.get_json()

        #validate the api key.
        key=id.get("api_key")
        user_id=id.get("user_id")
        order_id=id.get("order_id")

        #checking validity of the key.
        validity=validate_key(user_id,key)
        if validity.get("validity",False):
            api_response=my_api.status(order_id)
            return api_response
        else:
            return validity