import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import requests
import configparser
import os

class SubscriptionFormApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Subscription Form")

        # Load configurations from config.ini
        self.config = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")
        self.config.read(config_file_path)

        # Get form endpoint from config.ini
        self.host = self.config.get("Form", "host")
        self.port = self.config.getint("Form", "port")

        # Labels
        tk.Label(master, text="Client Name:").grid(row=0, column=0, sticky="w")
        tk.Label(master, text="Product Name:").grid(row=1, column=0, sticky="w")
        tk.Label(master, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        tk.Label(master, text="Index:").grid(row=3, column=0, sticky="w")

        # Entry fields
        self.client_name_entry = tk.Entry(master)
        self.client_name_entry.grid(row=0, column=1)

        self.product_name_entry = tk.Entry(master)
        self.product_name_entry.grid(row=1, column=1)

        self.end_date_entry = tk.Entry(master)
        self.end_date_entry.grid(row=2, column=1)

        self.index_entry = tk.Entry(master)
        self.index_entry.grid(row=3, column=1)

        # Buttons
        self.add_button = tk.Button(master, text="Add Subscription", command=self.add_subscription)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.view_button = tk.Button(master, text="View Subscriptions", command=self.view_subscriptions)
        self.view_button.grid(row=5, column=0, columnspan=2, pady=5)

        self.delete_button = tk.Button(master, text="Delete Subscription", command=self.delete_subscription)
        self.delete_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.renew_button = tk.Button(master, text="Renew Subscription", command=self.renew_subscription)
        self.renew_button.grid(row=7, column=0, columnspan=2, pady=5)

    def is_api_online(self):
        try:
            api_url = f"http://{self.host}:{self.port}"
            response = requests.get(api_url)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def add_subscription(self):
        try:
            index = int(self.index_entry.get())
            client_name = self.client_name_entry.get()
            product_name = self.product_name_entry.get()
            end_date_str = self.end_date_entry.get()

            if not self.is_api_online():
                messagebox.showerror("Error", "API is not online.")
                return

            # Check if the index already exists
            api_url = f"http://{self.host}:{self.port}/view_subscriptions"
            response = requests.get(api_url)
            if response.status_code == 200:
                subscriptions = response.json()
                indexes = [sub["index"] for sub in subscriptions]
                if index in indexes:
                    messagebox.showerror("Error", f"Subscription with index {index} already exists.")
                    return

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date < datetime.today().date():
                raise ValueError("End date cannot be in the past.")

            # Create new subscription dictionary
            new_subscription = {
                "index": index,
                "client_name": client_name,
                "product_name": product_name,
                "end_date": end_date_str
            }

            # Send the new subscription data to the API
            api_url = f"http://{self.host}:{self.port}/add_subscription"
            response = requests.post(api_url, json=new_subscription)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Subscription added successfully.")
            else:
                messagebox.showerror("Error", "Failed to add subscription.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def view_subscriptions(self):
        try:
            if not self.is_api_online():
                messagebox.showerror("Error", "API is not online.")
                return

            # Request the subscriptions data from the API
            api_url = f"http://{self.host}:{self.port}/view_subscriptions"
            response = requests.get(api_url)
            if response.status_code == 200:
                subscriptions = response.json()
                if subscriptions:
                    # Create a new window to display subscriptions
                    view_window = tk.Toplevel(self.master)
                    view_window.title("View Subscriptions")

                    # Labels for headers
                    tk.Label(view_window, text="Index").grid(row=0, column=0)
                    tk.Label(view_window, text="Client Name").grid(row=0, column=1)
                    tk.Label(view_window, text="Product Name").grid(row=0, column=2)
                    tk.Label(view_window, text="End Date").grid(row=0, column=3)

                    for i, subscription in enumerate(subscriptions, start=1):
                        tk.Label(view_window, text=subscription["index"]).grid(row=i, column=0)
                        tk.Label(view_window, text=subscription["client_name"]).grid(row=i, column=1)
                        tk.Label(view_window, text=subscription["product_name"]).grid(row=i, column=2)
                        tk.Label(view_window, text=subscription["end_date"]).grid(row=i, column=3)
                else:
                    messagebox.showinfo("Info", "No subscriptions available.")
            else:
                messagebox.showerror("Error", "Failed to retrieve subscriptions.")
        except requests.ConnectionError:
            messagebox.showerror("Error", "Failed to connect to the API.")

    def delete_subscription(self):
        try:
            if not self.is_api_online():
                messagebox.showerror("Error", "API is not online.")
                return

            # Retrieve the index of the subscription to delete
            index = simpledialog.askinteger("Delete Subscription", "Enter the index of the subscription to delete:")
            if index is not None:
                # Send a request to delete the subscription to the API
                api_url = f"http://{self.host}:{self.port}/delete_subscription"
                response = requests.post(api_url, json={"index": index})
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Subscription deleted successfully.")
                else:
                    messagebox.showerror("Error", "Failed to delete subscription.")
        except requests.ConnectionError:
            messagebox.showerror("Error", "Failed to connect to the API.")

    def renew_subscription(self):
        try:
            if not self.is_api_online():
                messagebox.showerror("Error", "API is not online.")
                return

            # Retrieve the index of the subscription to renew
            index = simpledialog.askinteger("Renew Subscription", "Enter the index of the subscription to renew:")
            if index is not None:
                # Retrieve new details for the subscription
                new_client_name = simpledialog.askstring("Renew Subscription", "Enter new client name:")
                new_product_name = simpledialog.askstring("Renew Subscription", "Enter new product name:")
                new_end_date = simpledialog.askstring("Renew Subscription", "Enter new end date (YYYY-MM-DD):")

                # Create the new subscription data
                renewed_subscription = {
                    "index": index,
                    "new_client_name": new_client_name,
                    "new_product_name": new_product_name,
                    "new_end_date": new_end_date
                }

                # Send a request to renew the subscription to the API
                api_url = f"http://{self.host}:{self.port}/renew_subscription"
                response = requests.post(api_url, json=renewed_subscription)
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Subscription renewed successfully.")
                else:
                    messagebox.showerror("Error", "Failed to renew subscription.")
        except requests.ConnectionError:
            messagebox.showerror("Error", "Failed to connect to the API.")

def main():
    root = tk.Tk()
    app = SubscriptionFormApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
