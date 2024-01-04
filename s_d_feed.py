import datetime
import schedule
import time
import threading
import requests
from orders import Order
from api_calls import ApiTable
from provider import Provider
from services import Service
from provider_api import Api

class MainScheduler:
    def drip_feed(self,quantity, interval,rate,api,data,order_id):
        o=Order()
        print("In the Drip Feed function")
        for i in range(0,int(rate)):
            response = api.order(data)
            if not response.get("error",False): 
                status=response.get("order","Pending")
                o.change_order_status(status, order_id)
                o.set_jap_order_id(response.get("orderId"),order_id)
            else:
                o.change_order_status("Failed", order_id)

        return response

    def execute_at_time(self,obj, make_order):
        execution_time_str = obj.execution_time
        execution_time = datetime.datetime.strptime(execution_time_str[:-4], '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.utcnow()
        delay = (execution_time - now).total_seconds()

        if delay < 0:
            print("The execution time is in the past. Executing immediately.")
            make_order(obj)
            return

        def delayed_execution():
            time.sleep(delay)
            make_order(obj)

        threading.Thread(target=delayed_execution).start()

    def make_order(self,order, comments="\n", runs=1, executions=1, usernames="", hashtags="", media="", max=100, min="", groups="", answer_number=""):
        print("In the make order function")
        # Get provider details
        p = Provider()
        provider_data = p.get_provider(order.package_id)
        api_key = provider_data[3]
        api_url = provider_data[2]

        # Set defaults for interval and rate if not provided
        interval = order.interval or 1
        rate = order.rate or 1

        # Get the service details
        s = Service(order.package_id)
        service_details = s.get_jap_service(order.service_id)

        # Initialize API with provider's key and URL
        api = Api(api_key, api_url)
        minimum_q = service_details[5]

        # Ensure quantity meets minimum requirements
        if order.quantity < minimum_q:
            order.quantity = minimum_q

        # Prepare data for API request
        data = {
            "service": service_details[8],
            "link": order.link,
            "quantity": order.quantity,
            "comments": order.comments,
            "action": "add",
            "usernames":usernames,
            "hashtags": hashtags,
            "media": media,
            "max": max,
            "runs": runs,
            "groups":groups,
            "answer_number":answer_number
        }

        # Execute the order
        self.drip_feed(order.quantity, order.interval, order.rate, api, data,order_id)

    def main(self):
        order_table=Order()
        api_table=ApiTable()
        records=api_table.get_all()
        call_ids=[]
        print("In the main function")

        for i in records:
            call_ids.append(i["call_id"])

        for call_id in call_ids:     
            all_orders=order_table.display_schedules(call_id)
            for i in all_orders:
                if i.order_status in ["failed","initiated","Cancelled"]:
                    self.execute_at_time(i,self.make_order)
                elif i.order_status in ["initiated"]:
                    self.execute_at_time(i,self.make_order)


    def schedule_and_execute_orders(self):

        print("The scheduler is now running and checking for changes.")

        schedule.run_all()
        while True:
            # Run the scheduled tasks
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        job = schedule.every(1).second.do(self.main)
        scheduler_thread = threading.Thread(target=self.schedule_and_execute_orders)
        scheduler_thread.start()