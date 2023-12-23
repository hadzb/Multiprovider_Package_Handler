from flask import Flask,jsonify,request,render_template,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from admin import admn_blueprint
from api_endpoints import api_blueprint
import requests
import keys
from api import Api
import json
import os
import uuid
import datetime
import database
import sqlite3
from orders import Order
from packages import Package
from scheduler import Scheduler
from orders import Order
from delivery_drip import DeliveryScheduler

API_KEY="3bb9c960c00b3469d7b70d7fbcc42f5b"
my_api=Api(API_KEY)
key=keys.KeyGen()
database=database.ApiDatabase()
app=Flask(__name__)
app.secret_key=os.urandom(24)

#registering the admn blueprint for handling admn requests.
app.register_blueprint(admn_blueprint,url_prefix="/admin")
app.register_blueprint(api_blueprint,url_prefix="/api")

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view='login'

#This is the user data model used for authentication.
class User(UserMixin,db.Model):
    id=db.Column(db.String(120),unique=True,nullable=False,primary_key=True)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(120),nullable=False)
    balance = db.Column(db.Integer, default=0) 

with app.app_context():
    db.create_all()

def generate_key():
    user_id=current_user.email
    api_key=str(uuid.uuid4())
    expiration_date=datetime.datetime.utcnow()+datetime.timedelta(days=30)
    
    with sqlite3.connect("file.db") as connection:
        try:

            cusor=connection.cursor()
            cusor.execute("INSERT INTO api_keys (user_id,api_key,expiration_date) VALUES (?,?,?)",(user_id,api_key,expiration_date))
            connection.commit()
        except sqlite3.IntegrityError as e:
            cusor.execute("UPDATE api_keys SET api_key=? WHERE user_id=?",(api_key,user_id))
            connection.commit()

        except sqlite3.OperationalError as e:
            with sqlite3.connect("file.db") as connection:
                cursor=connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys(
                        user_id TEXT PRIMARY KEY,
                        api_key TEXT,
                        expiration_date TEXT
                    )
                """)
                connection.commit()
                
    print("Generated API keys.")
    print(user_id)
    data={"api_key":api_key,"user_id":user_id,"expiry":str(expiration_date.date())}
    
    return data

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        #check if the email is registered
        if User.query.filter_by(email=email).first():
            flash("Email is already registered. Please use a different Email")
            print("Email is Already Registered")
        else:
            new_user=User(id=email,email=email,password=password,balance=1000)

            print("The new database user")
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            print("sign up completed")
            flash("Account Created Successfully")
            return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        #check if the user exists and password is correct
        user=User.query.filter_by(email=email).first()

        if user and user.password==password:
            login_user(user)
            print("Successfully logged in the user")
            flash("Login successful !","success")
            return redirect(url_for("hello"))
        else:
            
            return render_template("login.html",data={"error":"Invalid Username or Password"})

    return render_template("login.html")

@app.route("/")
@login_required
def hello():
    o=Order()
    data=dict()
    order_data=o.query_order_by_user(current_user.email)
    data["orders"]=order_data
    data["email"]=current_user.email
    
    d=get_api_keys(current_user.email)
    data["api_key"]=d["api_key"]
    data["expiry"]=d["expiry"]
    data["balance"]=current_user.balance

    return render_template("dashboard.html",data=data)

@app.route("/keys",methods=["POST","GET"])
@login_required
def generate():
    if request.method=="GET":
        return render_template("keys.html")
    else:
        #Generate a new set of keys for the user.
        result=generate_key()
        print(result)
        return jsonify(result)
    

@app.route("/logout")
def logout():
    logout_user()
    flash("logout was successful","success")
    return redirect(url_for("login"))


@app.route("/services",methods=["GET"])
@login_required
def services():
    api_response=my_api.services()
    return render_template("services.html",data=api_response)

@app.route("/order",methods=["POST","GET"])
@login_required
def add_order():
    if request.method=="GET":
        p=Package()
        packages=p.get_all_packages()
        s_id=[]

        for id in packages:
            item=dict()
            item["value"]=id[0]
            item["name"]=id[1]
            s_id.append(item)
        print(s_id)
        return render_template("form.html",data=s_id)

    else:
        post_data=request.get_json()
        order_table=Order()
        user_id=current_user.email
        package_id=post_data.get("service")
        s_id=package_id

        #Validate if the user has sufficient balance to make the calls
        if (validate_order(s_id,current_user.balance)):
            #get the package from the database.
            p=Package()
            package=p.get_package(package_id)
            providers=package[4].split("|")
            link=post_data.get("link","")
            comments=post_data.get("comments","\n")
            quantity=post_data.get("quantity",10)
            rate=""
            interval=""
            order_table=Order()
            for task in providers:
                package_id=task.split(":")[0]
                service_id=task.split(":")[1]
                prov_quantity=task.split(":")[2]
                order_status="initiated"
                user_id=current_user.email
                if int(prov_quantity)<int(quantity):
                    quantity=prov_quantity
                print(order_table.add_order(user_id,package_id,service_id,link,comments,quantity,rate,interval,order_status))
            return {"status":"sucesss","message":"Order was placed, check dashboard for progress"}
        else:
            return {"status":"failed","message":"Your account balance is insufficient"}
        
def validate_order(package_id,balance):
    p=Package()
    print(f"Getting Package of Package Id {package_id}")
    this_package=p.get_package(package_id)
    if this_package:
        print("Package has been Found")
        package_price=this_package[2]
        if balance-package_price<0:
            return False
        return True


@app.route("/balance",methods=["GET"])
@login_required
def get_balance():
    api_response=current_user.balance
    data=dict()
    data["balance"]=api_response
    data["currency"]="USD"
    data["email"]=current_user.email
    return render_template("user_balance.html",data=data)

@app.route("/status",methods=["POST","GET"])
@login_required
def get_status():
    if request.method=="POST":
        id=request.form.get("id")
        api_response=my_api.status(id)
        print(api_response)
        return render_template("status_.html",data=api_response)
    else:
        return render_template("status_form.html")

@app.route("/multi_status",methods=["POST"])
@login_required
def get_order_multi_status():
    data=request.get_json()
    response= my_api.multiStatus(data['order_ids'])
    return jsonify(response)

@app.route("/refill",methods=["POST"])
@login_required
def get_refill_status():
    api_response=my_api.refill(request.get_json()["refill"])
    return jsonify(api_response)

@app.route("/multi_refill",methods=["POST"])
@login_required
def get_refill_multi_status():
    data=request.get_json()
    response= my_api.multiRefill(data['order_ids'])
    return jsonify(response)

@app.route("/refill_status",methods=["POST"])
@login_required
def get_single_refill_status():
    return jsonify(my_api.refillStatus(request.get_json()["refill"]))

@app.route("/multi_refill_status",methods=["POST"])
@login_required
def get_multi_refill_status():
    data=request.json()
    response=my_api.multiRefillStatus(data["refill_ids"])

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
            response=my_api.order({"link":link,"comments":comments,"quantity":quantity,"action":"add","service":order_id})
            res_arr.append(response)
    return res_arr

def get_api_keys(user_id):
    with sqlite3.connect("file.db") as connection:
        cursor=connection.cursor()
        query="SELECT * FROM api_keys WHERE user_id=?"
        params=(user_id,)
        cursor.execute(query,params)
        data_=cursor.fetchone()

        data=dict()
        if data:
            data["api_key"]=data_[1]
            data["expiry"]=data_[2]
        else:
            data["api_key"]="****************************"
            data["expiry"]="*****************************"

    return data
    


if __name__=="__main__":
    a=Scheduler()
    delivery=DeliveryScheduler()

    # a.run()
    delivery.run()

    app.run(debug=True)