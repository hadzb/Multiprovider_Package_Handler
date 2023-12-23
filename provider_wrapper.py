from provider import Provider
from provider_api import Api

class ProviderWrapper:
    def __init__(self,provider_id):
        provider_id=provider_id
        database=Provider()
        credentials=database.get_provider(provider_id)
        self.api=Api(credentials[3],credentials[2])

    def get_all_services(self):
        services=self.api.services()
        return services

    def get_balance(self):
        balance=self.api.balance()
    
    def make_order(self,data):
        return self.api.order(data)
    
    def get_order_status(self,order_id):
        return self.api.status(order_id)