import schedule
import time
from orders import Order
from provider_api import Api
from services import Service
from provider import Provider
import threading

class Scheduler():

    def construct_service_object(self, service):
        return {
            "service_id": service[0],
            "cancel": service[1],
            "category": service[2],
            "dripfeed": service[3],
            "max": service[4],
            "min": service[5],
            "name": service[6],
            "refill": service[7],
            "service": service[8],
            "type": service[9],
            "rate": service[10],
            "interval": service[11]
        }

    def make_order(self,comments="\n", runs=1, executions=1, usernames="", hashtags="", media="", max=100, min="", groups="", answer_number=""):

        o = Order()
        orders = o.get_pending_orders()

        for order in orders:
            order_id, user_id, provider_id, service_id, link, comments, quantity, rate, interval, order_status = order
            p = Provider()
            p_data = p.get_provider(provider_id)
            api_key = p_data[3]
            api_url = p_data[2]

            if interval == "":
                interval = 1
            if rate == "":
                rate = 1

            p = Provider()
            p_ = p.get_provider(provider_id)
            api_key = p_[3]
            api_url = p_[2]

            # Get the service Requirements
            s = Service(provider_id)
            service_details = s.get_jap_service(service_id)

            api = Api(api_key, api_url)
            minimum_q = service_details[5]

            # Check if the quantity is less than the minimum quantity, if that is the case, let it be the minimum quantity described by the service.
            if quantity < minimum_q:
                quantity = minimum_q

            data = {
                "service": service_details[8],
                "link": link,
                "quantity": quantity,
                "comments": comments,
                "action": "add",
                "usernames": usernames,
                "hashtags": hashtags,
                "media": media,
                "max": max,
                "runs": runs,
                "min": service_details[5],
                "groups": groups,
                "answer_number": answer_number
            }
            self.drip_feed(quantity,interval,rate,api,data)

    def drip_feed(self,quantity, interval,rate,api,data):
        for i in range(0,rate):
            response = api.order(data)
            if not response.get("error", False):
                o.change_order_status("running", order_id)
            else:
                o.change_order_status("Failed", order_id)
        return response

    def schedule_and_execute_orders(self):
        print("The scheduler is now running and checking for changes.")

        schedule.run_all()

        while True:
            # Run the scheduled tasks
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        job = schedule.every(1).second.do(self.make_order)
        scheduler_thread = threading.Thread(target=self.schedule_and_execute_orders)
        scheduler_thread.start()