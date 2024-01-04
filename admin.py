from flask import Blueprint,render_template,request,redirect
import sqlite3
from provider import Provider
from provider_wrapper import Api
from services import Service
from packages import Package
from orders import Order
from api_calls import ApiTable
from urllib.parse import unquote
from itertools import groupby

database=Provider()
admn_blueprint=Blueprint("admn_blueprint",__name__)

def initialize_service():
    with sqlite3.connect("file.db") as connection:
        try:
            cusor=connection.cursor()
            service_query="""CREATE TABLE IF NOT EXISTS services(
                service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                jap_id TEXT,
                service_name TEXT,
                service_price REAL,
                service_rate  REAL,
                min INTEGER,
                max INTEGER,
                type TEXT
            )"""
            cusor.execute(service_query)
            connection.commit()
        except Exception as e:
            print(e)
            
initialize_service()
@admn_blueprint.route("/createserv",methods=["POST","GET"])
def create_service():
    if request.method=="POST":
        jap_id=request.form.get("jap_id")
        service_name=request.form.get("service_name")
        service_price=request.form.get("service_price")
        service_rate=request.form.get("service_rate")
        min=request.form.get("min")
        max=request.form.get("max")

        with sqlite3.connect("file.db") as connection:
            try:
                cusor=connection.cursor()
                query="INSERT INTO services (jap_id,service_name,service_price,service_rate,min,max,type) VALUES (?,?,?,?,?,?,?)"
                params=(jap_id,service_name,service_price,service_rate,min,max,"service")
                cusor.execute(query,params)
                print("Added a new service to the database")
            except Exception as e:
                print(e)

        return redirect("http://13.53.111.198/admin/serv")
    else:
        return render_template("create_service.html")
    
def parse_configuration(string_input):
    cat_provider=string_input.split("|")
    configuration=[]

    for config in cat_provider:
        mini_config=dict()
        data=config.split(":")
        mini_config["provider_id"]=data[0]
        mini_config["service_id"]=data[1]
        mini_config["quantity"]=data[2]
        mini_config["interval"]=data[3]
        mini_config["rate"]=data[4]

        configuration.append(mini_config)

    return configuration

@admn_blueprint.route("/serv",methods=["GET"])
def get_services():
    #Query the database for all services
    with sqlite3.connect("file.db") as connection:
        try:
            cusor=connection.cursor()
            query="SELECT * FROM services WHERE type=?"
            cusor.execute(query,("service",))
            data=cusor.fetchall()
            all_data=[]
            for i in data:
                parsed_data=dict()
                parsed_data["service_id"]=i[0]
                parsed_data["jap_id"]=i[1]
                parsed_data["service_name"]=i[2]
                parsed_data["service_price"]=i[3]
                parsed_data["service_rate"]=i[4]
                parsed_data["min"]=i[5]
                parsed_data["max"]=i[6]
                all_data.append(parsed_data)
            print(all_data)
            return render_template("services.html",data=all_data)

        except Exception as e:
            print(e)   

@admn_blueprint.route("/createpkg",methods=["GET","POST"])
def create_package():
    if request.method=="GET":
        #collect all the providers
        database=Provider()
        all_providers=database.get_all_providers()
        data=dict()
        data["providers"]=parse_package_response(all_providers)
        data["services"]=[{}]
        data["categories"]=get_categories(parse_service_response(data["providers"]))
        return render_template("form_create_package.html",data=data)
    else:

        providers=request.form.getlist('providers')
        services=request.form.getlist('services')
        quantities=request.form.getlist('quantity')
        intervals=request.form.getlist('interval')
        rates=request.form.getlist('rate')


        print(f"providers ... {providers}")
        print(f"services ... {services}")
        print(f"quantities ... {quantities}")


        package_name=request.form.get("name")
        package_price=request.form.get("price")
        package_rate=request.form.get("rate")
        package_interval=request.form.get("interval")
        
        package_info=[]
        for provider,service,quantity,interval,rate in zip(providers,services,quantities,intervals,rates):
            actual_id=service
            package_info.append(f"{provider}:{actual_id}:{quantity}:{interval}:{rate}")
            print(package_info)

        package_info="|".join(package_info)
        print(package_info)

        # Saving the Package to Database
        p=Package()
        p.add_package(package_name,package_price,package_rate,package_interval,package_info)

        all_packages=p.get_all_packages()
        all_data=[]

        for i in all_packages:
            parsed_data=dict()
            parsed_data["package_id"]=i[0]
            parsed_data["package_name"]=i[1]
            parsed_data["package_price"]=i[2]
            parsed_data["package_provider"]=i[3]
            parsed_data["package_configuration"]=parse_configuration(parsed_data["package_provider"])
            
            all_data.append(parsed_data)
    
        return render_template("_providers.html",data=all_data)

@admn_blueprint.route("/orders",methods=["GET","POST"])
def get_orders():
    o=Order()
    orders=o.get_all_orders()
    collection=[]
    for i in orders:
        item=dict()
        item["order_id"]=i[0]
        item["user_id"]=i[1]
        item["package_id"]=i[2]
        item["service_id"]=i[3]
        item["link"]=i[4]
        item["comments"]=i[5]
        item["quantity"]=i[6]
        item["rate"]=i[7]
        item["interval"]=i[8]
        item["order_status"]=i[9]
        collection.append(item)
    return render_template("orders.html",data=collection)


@admn_blueprint.route("/keys", methods={"GET"})
def get_keys():
    with sqlite3.connect("file.db") as connection:
        cursor=connection.cursor()
        cursor.execute("SELECT * FROM api_keys")
        data=cursor.fetchall()
        collection=[]
        for i in data:
            item=dict()
            item["user_id"]=i[0]
            item["api_key"]=i[1]
            item["expiry"]=i[2]
            collection.append(item)
        return render_template("api_keys_table.html",data=collection)

@admn_blueprint.route("/users")
def get_users():
    with sqlite3.connect(r"./instance/users.db") as connection:
        cursor=connection.cursor()
        cursor.execute("SELECT * FROM user")
        data=cursor.fetchall()
        collection=[]
        for i in data:
            item=dict()
            item["user_id"]=i[0]
            item["email"]=i[1]
            item["password"]=i[2]
            collection.append(item)
        return render_template("users_table.html",data=collection)

@admn_blueprint.route("/packages")
def get_packages():
    with sqlite3.connect("file.db") as connection:
        cursor=connection.cursor()
        cursor.execute("SELECT * FROM services WHERE type=?",("package",))
        data=cursor.fetchall()
        collection=[]
        a=Package()
        packages=a.get_all_packages()
        for i in packages:
            parsed_data=dict()
            parsed_data["package_id"]=i[0]
            parsed_data["package_name"]=i[1]
            parsed_data["package_price"]=i[2]
            parsed_data["package_provider"]=i[3]
            parsed_data["package_configuration"]=parse_configuration(parsed_data["package_provider"])

            collection.append(parsed_data)
            print(collection)
        return render_template("_providers.html",data=collection)

@admn_blueprint.route("/deletepackage/<int:entry_id>",methods=["GET"])
def delete_package(entry_id=""):
    if request.method=="GET":
        a=Package()
        a.delete_package(entry_id)
        return redirect("http://13.53.111.198/admin/packages")


@admn_blueprint.route("/editpackage",methods=["POST"])
def edt_package():
        provider_id=request.form.get("provider_id")
        provider_name=request.form.get("provider_name")
        provider_url=request.form.get("provider_url")
        provider_key=request.form.get("provider_key")
        print((provider_name,provider_url,provider_key,provider_id))

        response=database.edit_provider((provider_name,provider_url,provider_key,provider_id))

        if response["status"]==True:
            providers=database.get_all_providers()
            collection=[]
            for provider in providers:
                prov=dict()
                prov["provider_id"]=provider[0]
                prov["provider_name"]=provider[1]
                prov["provider_url"]=provider[2]
                prov["provider_key"]=provider[3]
                collection.append(prov)
            return render_template("packages.html",data=collection)
        else:
            return {"error":"could not parse the response"}
        
@admn_blueprint.route("/providers",methods=["GET","POST"])
def get_providers():
    if request.method=="GET":
        providers=database.get_all_providers()
        collection=[]
        for provider in providers:
            prov=dict()
            prov["provider_id"]=provider[0]
            prov["provider_name"]=provider[1]
            prov["provider_url"]=provider[2]
            prov["provider_key"]=provider[3]
            collection.append(prov)
        return render_template("providers.html",data=collection)

    else:
        provider_name=request.form.get("provider_name")
        provider_url=request.form.get("provider_url")
        provider_key=request.form.get("provider_key")
        response=database.add_provider(provider_name,provider_url,provider_key)

        provider_id=response["provider_id"]
        a=Service(provider_id)
        a.initialize_services()
        serv=a.get_all_services()
        
        #Print all the services.
        print(serv)

        if response["status"]==True:
            providers=database.get_all_providers()
            collection=[]
            for provider in providers:
                prov=dict()
                prov["provider_id"]=provider[0]
                prov["provider_name"]=provider[1]
                prov["provider_url"]=provider[2]
                prov["provider_key"]=provider[3]
                collection.append(prov)

        
            return render_template("providers.html",data=collection)
        else:
            return {"error":"could not parse the response"}

@admn_blueprint.route("/editprovider/<int:entry_id>",methods=["GET","POST"])
def edit_provider(entry_id=""):
    if request.method=="GET":
        entry=database.get_provider(str(entry_id))
        if entry:
            data=dict()
            data["provider_id"]=entry[0]
            data["provider_name"]=entry[1]
            data["provider_url"]=entry[2]
            data["provider_key"]=entry[3]
            return render_template("update_provider.html",data=data)

        else:
            print("Element does not exist in the database.")
            return redirect("http://13.53.111.198/admin/providers")

@admn_blueprint.route("/editprovider",methods=["POST"])
def edt_provider():
        provider_id=request.form.get("provider_id")
        provider_name=request.form.get("provider_name")
        provider_url=request.form.get("provider_url")
        provider_key=request.form.get("provider_key")

        print((provider_name,provider_url,provider_key,provider_id))

        response=database.edit_provider((provider_name,provider_url,provider_key,provider_id))

        if response["status"]==True:
            providers=database.get_all_providers()
            collection=[]
            for provider in providers:
                prov=dict()
                prov["provider_id"]=provider[0]
                prov["provider_name"]=provider[1]
                prov["provider_url"]=provider[2]
                prov["provider_key"]=provider[3]
                collection.append(prov)
            return render_template("providers.html",data=collection)
        else:
            return {"error":"could not parse the response"}

@admn_blueprint.route("/deleteprovider/<int:entry_id>",methods=["GET"])
def delete_provider(entry_id=""):
    if request.method=="GET":
        database.delete_provider(entry_id)
        return redirect("http://13.53.111.198/admin/providers")

@admn_blueprint.route("/balance/<int:entry_id>",methods=["GET"])
def get_balance(entry_id):
    #get the api_key
    database=Provider()
    entry=database.get_provider(entry_id)
    provider_key=entry[3]
    provider_url=entry[2]
    myapi=Api(provider_key,provider_url)
    print(myapi.balance())
    data=myapi.balance()

    return render_template("balance.html",data=data)

@admn_blueprint.route("/services/<int:entry_id>",methods=["GET"])
def get_all_services(entry_id):
    a=Service(entry_id)
    a.initialize_services()
    serv=a.get_all_services()

    return render_template("provider_services.html",data=serv)

def parse_package_response(data):
    collection=[]
    for provider in data:
        prov=dict()
        prov["provider_id"]=provider[0]
        prov["provider_name"]=provider[1]
        prov["provider_url"]=provider[2]
        prov["provider_key"]=provider[3]
        collection.append(prov)

    return collection

def parse_service_response(providers):
    all_services=[]
    for provider in providers:
        data=dict()
        provider_id=provider.get("provider_id")
        myapi=Api(provider.get("provider_key"),provider.get("provider_url"))
        services=myapi.services()
        data[f"{provider_id}"]=services

        all_services.append(data)

    return all_services


#Takes as parameter packages : A collection of package Ids, and services a collection of dictionaries
def get_categories(services): 
    cat_data=dict()
    for service in services:
        #get the key for the provider
        key=list(service.keys())[0]

        categories=[]
        for service_ in service.get(key):
            category=service_.get("category")
            if category not in categories:
                categories.append(category)
        cat_data[key]=categories 

    return cat_data  

@admn_blueprint.route("/getcat/<int:provider_id>")
def pass_categories(provider_id):
    all_categories=[]
    if(provider_id):     
        a=Service(provider_id)
        services=a.get_all_services()
        for service in services:
            service_category=service.get("category")
            if service_category not in all_categories:
                all_categories.append(service_category)
    return all_categories

def groupServicesByCategory(objects):
    objects.sort(key=lambda x: x['category'])
    grouped_objects = {key: list(group) for key, group in groupby(objects, key=lambda x: x['category'])}
    return grouped_objects

@admn_blueprint.route("/getserv/<path:category>/<int:provider>")
def get_services_(category,provider):
    category=unquote(category)
    a=Service(provider)
    all_services=a.get_all_services()
    categories=groupServicesByCategory(all_services)
    return categories.get(category)

@admn_blueprint.route("/getcall/<int:id>")
def get_callId(id):
    table=Order()
    order_objects=table.display_schedules(id)
    json_list = []
    for order_object in order_objects:
        order_dict = {
            "order_id": order_object.order_id,
            "user_id": order_object.user_id,
            "package_id": order_object.package_id,
            "service_id": order_object.service_id,
            "link": order_object.link,
            "comments": order_object.comments,
            "quantity": order_object.quantity,
            "rate": order_object.rate,
            "interval": order_object.interval,
            "call_id": order_object.call_id,
            "order_status": order_object.order_status,
            "execution_time": order_object.execution_time,
            "start":order_object.order_start,
            "provider_name":order_object.provider_name,
            "jap_order_id":order_object.jap_order_id
        }
        json_list.append(order_dict)
    return render_template("scheduled_orders.html",data=json_list)

@admn_blueprint.route("/")
def admnDashboard():    
    #for the packages
    a=Package()
    packages=a.get_all_packages()
    package_collection=[]
    for i in packages:
        parsed_data=dict()
        parsed_data["package_id"]=i[0]
        parsed_data["package_name"]=i[1]
        parsed_data["package_price"]=i[2]
        parsed_data["package_provider"]=i[3]
        package_collection.append(parsed_data)

    #for the orders       
    o=Order()
    table=ApiTable()
    orders=table.get_all()
    order_collection=orders

    #for the providers
    providers=database.get_all_providers()
    provider_collection=[]
    for provider in providers:
        prov=dict()
        prov["provider_id"]=provider[0]
        prov["provider_name"]=provider[1]
        prov["provider_url"]=provider[2]
        prov["provider_key"]=provider[3]
        provider_collection.append(prov)

    with sqlite3.connect("file.db") as connection:
        cursor=connection.cursor()
        query="SELECT * FROM api_keys"
        cursor.execute(query)
        all_users=cursor.fetchall()

        user_collection=[]
        for i in all_users:
            user=dict()
            user["id"]=i[0]
            user["key"]=i[1]
            user["expiry"]=i[2]
            user_collection.append(user)
        
    fields=dict()
    fields["orders"]=order_collection
    fields["providers"]=provider_collection
    fields["packages"]=package_collection
    fields["users"]=user_collection
    data=fields

    return render_template("admnDashboard.html",data=data)
