import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import requests
import configparser
import os
import sys

class SubscriptionFormApp:
    def __init__(self, master):
        self.master = master
        master.title("Subscription Form")

        # Get the directory of the script
        if getattr(sys, 'frozen', False):
            # Running in a bundle
            self.script_dir = os.path.dirname(sys.executable)
        else:
            # Running in normal Python environment
            self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Load configurations from config.ini
        config_file_path = os.path.join(self.script_dir, "config.ini")

        # Create config file if it doesn't exist
        if not os.path.exists(config_file_path):
            self.create_config_file(config_file_path)

        # Load configurations from config.ini
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

        # Get form endpoint from config.ini
        self.host = self.config.get("Form", "host")
        self.port = self.config.getint("Form", "port")

        # Labels
        tk.Label(master, text="Client Name:").grid(row=0, column=0, sticky="w")
        tk.Label(master, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")

        # Entry fields
        self.client_name_entry = tk.Entry(master)
        self.client_name_entry.grid(row=0, column=1)

        # Product Listbox
        tk.Label(master, text="Products:").grid(row=3, column=0, sticky="w")
        self.product_listbox = tk.Listbox(master, selectmode=tk.SINGLE)
        self.product_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.product_listbox.bind("<<ListboxSelect>>", self.on_product_select)  # Bind function to listbox
        self.update_product_list()  # Update the product list initially
        self.selected_product = None  # Variable to store selected product

        # Entry field for new product
        tk.Label(master, text="New Product:").grid(row=5, column=0, sticky="w")
        self.new_product_entry = tk.Entry(master)
        self.new_product_entry.grid(row=5, column=1, padx=1, pady=5, sticky="ew")

        # Button to add new product
        self.add_product_button = tk.Button(master, text="Add Product", command=self.add_product)
        self.add_product_button.grid(row=5, column=2, padx=1, pady=1, sticky="ew")

        # Entry field for end date
        self.end_date_entry = tk.Entry(master)
        self.end_date_entry.grid(row=2, column=1)

        # Buttons
        self.add_button = tk.Button(master, text="Add Subscription", command=self.add_subscription)
        self.add_button.grid(row=6, column=0, columnspan=2, pady=5)

        self.view_button = tk.Button(master, text="View Subscriptions", command=self.view_subscriptions)
        self.view_button.grid(row=7, column=0, columnspan=2, pady=5)

        self.delete_button = tk.Button(master, text="Delete Subscription", command=self.delete_subscription)
        self.delete_button.grid(row=8, column=0, columnspan=2, pady=5)

        self.renew_button = tk.Button(master, text="Renew Subscription", command=self.renew_subscription)
        self.renew_button.grid(row=9, column=0, columnspan=2, pady=5)

        # Check API status
        self.check_api_status()

    def check_api_status(self):
        try:
            api_url = f"http://{self.host}:{self.port}/is_api_online"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for non-OK responses
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the API: {e}")

    def add_subscription(self):
        client_name = self.client_name_entry.get().strip()
        selected_product = self.product_listbox.get(tk.ACTIVE)
        end_date_str = self.end_date_entry.get().strip()

        print(f"Client Name: {client_name}")
        print(f"Selected Product: {selected_product}")
        print(f"End Date: {end_date_str}")

        if not all([client_name, selected_product, end_date_str]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            # Check API status
            self.check_api_status()

            # Validate end date
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date < datetime.today().date():
                raise ValueError("End date cannot be in the past.")

            # Send request to add subscription
            api_url = f"http://{self.host}:{self.port}/add_subscription"
            new_subscription = {
                "client_name": client_name,
                "product_name": selected_product,
                "end_date": end_date_str
            }
            print("Sending request:", new_subscription)
            response = requests.post(api_url, json=new_subscription)
            response.raise_for_status()  # Raise an error for non-OK responses
            messagebox.showinfo("Success", "Subscription added successfully.")
        except (ValueError, requests.RequestException) as e:
            messagebox.showerror("Error", str(e))



    def view_subscriptions(self):
        try:
            # Check API status
            self.check_api_status()

            # Request the subscriptions data from the API
            api_url = f"http://{self.host}:{self.port}/view_subscriptions"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for non-OK responses

            # Show subscriptions in a new window
            subscriptions = response.json()
            if subscriptions:
                view_window = tk.Toplevel(self.master)
                view_window.title("View Subscriptions")

                # Labels for headers
                tk.Label(view_window, text="Index").grid(row=0, column=0)
                tk.Label(view_window, text="Client Name").grid(row=0, column=1)
                tk.Label(view_window, text="Product Name").grid(row=0, column=2)
                tk.Label(view_window, text="End Date").grid(row=0, column=3)

                # Display subscription data
                for i, subscription in enumerate(subscriptions, start=1):
                    tk.Label(view_window, text=subscription["index"]).grid(row=i, column=0)
                    tk.Label(view_window, text=subscription.get("client_name", "")).grid(row=i, column=1)
                    tk.Label(view_window, text=subscription.get("product_name", "")).grid(row=i, column=2)
                    tk.Label(view_window, text=subscription.get("end_date", "")).grid(row=i, column=3)
            else:
                messagebox.showinfo("Info", "No subscriptions available.")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to retrieve subscriptions: {e}")


    def delete_subscription(self):
        try:
            # Check API status
            self.check_api_status()

            # Retrieve the index of the subscription to delete
            index = simpledialog.askinteger("Delete Subscription", "Enter the index of the subscription to delete:")
            if index is not None:
                # Send a request to delete the subscription
                api_url = f"http://{self.host}:{self.port}/delete_subscription"
                response = requests.post(api_url, json={"index": index})
                response.raise_for_status()  # Raise an error for non-OK responses
                messagebox.showinfo("Success", "Subscription deleted successfully.")
        except (ValueError, requests.RequestException) as e:
            messagebox.showerror("Error", str(e))

    def renew_subscription(self):
        try:
            # Check API status
            self.check_api_status()

            # Retrieve the index of the subscription to renew
            index = simpledialog.askinteger("Renew Subscription", "Enter the index of the subscription to renew:")
            if index is not None:
                # Retrieve new end date for the subscription
                new_end_date = simpledialog.askstring("Renew Subscription", "Enter new end date (YYYY-MM-DD):")

                if not new_end_date:
                    messagebox.showerror("Error", "Please enter a new end date.")
                    return

                # Validate the new end date
                datetime.strptime(new_end_date, "%Y-%m-%d")

                # Send a request to renew the subscription
                api_url = f"http://{self.host}:{self.port}/renew_subscription"
                renewed_subscription = {"index": index, "new_end_date": new_end_date}
                response = requests.post(api_url, json=renewed_subscription)
                response.raise_for_status()  # Raise an error for non-OK responses
                messagebox.showinfo("Success", "Subscription renewed successfully.")

                # Refresh view after renewing subscription
                self.view_subscriptions()
        except (ValueError, requests.RequestException) as e:
            messagebox.showerror("Error", str(e))

    def add_product(self):
        new_product = self.new_product_entry.get().strip()
        if new_product:
            try:
                # Check API status
                self.check_api_status()

                # Send request to add product
                api_url = f"http://{self.host}:{self.port}/add_product"
                response = requests.post(api_url, json={"product_name": new_product})
                response.raise_for_status()  # Raise an error for non-OK responses
                messagebox.showinfo("Success", "Product added successfully.")
                self.update_product_list()  # Update the product list after adding a new product
            except requests.RequestException as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")
        else:
            messagebox.showerror("Error", "Please enter a product name.")

    def on_product_select(self, event):
        # Function to update selected_product variable when an item in the listbox is selected
        index = self.product_listbox.curselection()
        if index:
            self.selected_product = self.product_listbox.get(index)

    def update_product_list(self):
        try:
            # Request the product list from the API
            api_url = f"http://{self.host}:{self.port}/get_products"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for non-OK responses

            # Update the product list in the GUI
            products = response.json()
            self.product_listbox.delete(0, tk.END)  # Clear the current list
            for product in products:
                self.product_listbox.insert(tk.END, product)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to retrieve products: {e}")

    def create_config_file(self, config_file_path):
        # Create a default config file
        config = configparser.ConfigParser()
        config["Form"] = {"host": "0.0.0.0", "port": "5002"}
        with open(config_file_path, "w") as configfile:
            config.write(configfile)

def main():
    root = tk.Tk()
    app = SubscriptionFormApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
