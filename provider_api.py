import requests

class Api:
    def __init__(self, api_key: str,api_url):
        self.api_url = api_url
        self.api_key = api_key

    def services(self):
        post_data = {'key': self.api_key, 'action': 'services'}
        response = self.connect(post_data)
        return response

    def connect(self,data):
        data=data
        response=requests.post(self.api_url,data)
        return response.json()

    def order(self,data):
        data["key"]=self.api_key
        print(data)
        return self.connect(data)
    
    def status(self,order_id):
        post_data={"key":self.api_key,"action":"status","order":order_id}
        response=self.connect(post_data)
        return response

    def multiStatus(self,order_ids):
        orders=",".join(map(str,order_ids))
        post_data={"key":self.api_key,"action":"status","orders":orders}
        response=self.connect(post_data)
        return response

    def refill(self,order_id):
        post_data={"key":self.api_key,"order":order_id}
        response=self.connect(post_data)
        return response

    def multiRefill(self,order_ids):
        orders=",".join(map(str,order_ids))
        post_data={"key":self.api_key,"orders":orders}
        response=self.connect(post_data)
        return response
    
    def refillStatus(self,refill_id):
        post_data={"key":self.api_key,"refill":refill_id}
        response=self.connect(post_data)
        return response
    
    def multiRefillStatus(self,refill_ids):
        refills=",".join(map(str,refill_ids))
        post_data={"key":self.api_key,"refills":refills}
        response=self.connect(post_data)
        return response
    
    def balance(self):
        post_data={"key":self.api_key,"action":"balance"}
        response=self.connect(post_data)
        return response