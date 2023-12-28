import sqlite3
import pandas as pd
import schedule
import threading
import time

class DeliveryScheduler:

    def update_interval_column(self,file_path="file.db"):
        # Connect to the SQLite database
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        # Read the contents of the "orders" table into a Pandas DataFrame
        query = 'SELECT * FROM orders WHERE order_status = "initiated"'
        df = pd.read_sql_query(query, conn)

        if df.empty==False:
            # Filter rows with non-null comments
            non_null_comments = df[df['comments'].notnull()]

            # Sample 20% of rows with non-null comments
            sample_size = int(0.2 * len(non_null_comments))
            sample_rows = non_null_comments.sample(n=sample_size, random_state=42)

            # Set interval column to 1 for the sampled rows, and 20 for the rest
            df['interval'] = 20
            df['order_status']='scheduled'
            df.loc[sample_rows.index, 'interval'] = 3600

            # Update the "orders" table with the modified DataFrame
            cursor.execute('DROP TABLE IF EXISTS orders')
            df.to_sql('orders', conn, index=False)

            # Commit changes and close the connection
            conn.commit()
            conn.close()


    def schedule_and_execute_orders(self):
        print("The Delivery Module is now running and checking for changes.")

        while True:
            # Run the scheduled tasks
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        job = schedule.every(10).seconds.do(self.update_interval_column)
        scheduler_thread = threading.Thread(target=self.schedule_and_execute_orders)
        scheduler_thread.start()