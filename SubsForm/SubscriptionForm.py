import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import requests
import configparser
import os
import sys

class SubscriptionFormApp:
    def __init__(self, master):
        self.master = master
        self.search_var = tk.StringVar()
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

        # Create a frame for the form
        self.form_frame = ttk.Frame(master, padding="20")
        self.form_frame.grid(row=0, column=0, sticky="nsew")
        self.form_frame.columnconfigure(1, weight=1)  # Make column 1 expandable

        # Client Name
        ttk.Label(self.form_frame, text="Client Name:").grid(row=0, column=0, sticky="w")
        self.client_name_entry = ttk.Entry(self.form_frame)
        self.client_name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        # End Date
        ttk.Label(self.form_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.end_date_entry = ttk.Entry(self.form_frame)
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        # Products Label
        ttk.Label(self.form_frame, text="Products:").grid(row=2, column=0, sticky="w")

        # Product Listbox
        self.product_listbox = tk.Listbox(self.form_frame, selectmode=tk.SINGLE)
        self.product_listbox.grid(row=3, column=0, columnspan=2, padx=(0, 10), pady=5, sticky="nsew")
        self.product_listbox.bind("<<ListboxSelect>>", self.on_product_select)  # Bind function to listbox
        self.update_product_list()  # Update the product list initially

        # New Product Entry
        ttk.Label(self.form_frame, text="New Product:").grid(row=4, column=0, sticky="w")
        self.new_product_entry = ttk.Entry(self.form_frame)
        self.new_product_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10))

        # Add Product Button
        self.add_product_button = ttk.Button(self.form_frame, text="Add Product", command=self.add_product)
        self.add_product_button.grid(row=4, column=2, sticky="ew", padx=(0, 10))

        # Delete Product Button
        self.delete_product_button = ttk.Button(self.form_frame, text="Delete Product", command=self.delete_product)
        self.delete_product_button.grid(row=4, column=3, sticky="ew", padx=(0, 10))

        # Buttons Frame
        self.buttons_frame = ttk.Frame(master)
        self.buttons_frame.grid(row=1, column=0, pady=(10, 0))
        self.buttons_frame.columnconfigure((0, 1, 2, 3), weight=1)  # Make all columns expandable

        # Add Subscription Button
        self.add_button = ttk.Button(self.buttons_frame, text="Add Subscription", command=self.add_subscription)
        self.add_button.grid(row=0, column=0, pady=5, padx=(0, 5), sticky="ew")

        # View Subscriptions Button
        self.view_button = ttk.Button(self.buttons_frame, text="View Subscriptions", command=self.view_subscriptions)
        self.view_button.grid(row=0, column=1, pady=5, padx=(0, 5), sticky="ew")

        # Delete Subscription Button
        self.delete_button = ttk.Button(self.buttons_frame, text="Delete Subscription", command=self.delete_subscription)
        self.delete_button.grid(row=0, column=2, pady=5, padx=(0, 5), sticky="ew")

        # Renew Subscription Button
        self.renew_button = ttk.Button(self.buttons_frame, text="Renew Subscription", command=self.renew_subscription)
        self.renew_button.grid(row=0, column=3, pady=5, padx=(0, 5), sticky="ew")

        # Check API status
        self.check_api_status()

    def check_api_status(self):
        try:
            api_url = f"http://{self.host}:{self.port}/is_api_online"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for non-OK responses
        except requests.RequestException as e:
            self.handle_error("Error", f"Failed to connect to the API: {e}")

    def add_subscription(self):
        client_name = self.client_name_entry.get().strip()
        selected_product = self.product_listbox.get(tk.ACTIVE)
        end_date_str = self.end_date_entry.get().strip()

        print(f"Client Name: {client_name}")
        print(f"Selected Product: {selected_product}")
        print(f"End Date: {end_date_str}")

        if not all([client_name, selected_product, end_date_str]):
            self.handle_error("Error", "Please fill in all fields.")
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
            self.handle_error("Error", str(e))

    def view_subscriptions(self):
        try:
            # Check API status
            self.check_api_status()

            # Request the subscriptions data from the API
            api_url = f"http://{self.host}:{self.port}/view_subscriptions"
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an error for non-OK responses

            # Get the subscriptions from the response
            subscriptions = response.json()

            if subscriptions:
                # Create a Toplevel window for view subscriptions
                view_window = tk.Toplevel(self.master)
                view_window.title("View Subscriptions")

                # Get screen width and height
                screen_width = view_window.winfo_screenwidth()
                screen_height = view_window.winfo_screenheight()

                # Calculate position for centering the window
                x = (screen_width - view_window.winfo_reqwidth()) // 2
                y = (screen_height - view_window.winfo_reqheight()) // 2

                # Set window position
                view_window.geometry("+{}+{}".format(x, y))

                # Frame to hold search and subscriptions
                search_frame = ttk.Frame(view_window)
                search_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

                # Search Entry
                search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
                search_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

                # Search Button
                search_button = ttk.Button(search_frame, text="Search", command=self.filter_subscriptions)
                search_button.grid(row=0, column=1, padx=(5, 0))

                # Frame to hold subscriptions
                subscriptions_frame = ttk.Frame(view_window)
                subscriptions_frame.grid(row=1, column=0, columnspan=4)

                # Labels for headers
                ttk.Label(subscriptions_frame, text="Index").grid(row=0, column=0)
                ttk.Label(subscriptions_frame, text="Client Name").grid(row=0, column=1)
                ttk.Label(subscriptions_frame, text="Product Name").grid(row=0, column=2)
                ttk.Label(subscriptions_frame, text="End Date").grid(row=0, column=3)

                subscription_widgets = []  # To store widgets of subscriptions

                for i, subscription in enumerate(subscriptions, start=1):
                    # Create widgets for each subscription
                    index_label = ttk.Label(subscriptions_frame, text=subscription["index"])
                    client_name_label = ttk.Label(subscriptions_frame, text=subscription.get("client_name", ""))
                    product_name_label = ttk.Label(subscriptions_frame, text=subscription.get("product_name", ""))
                    end_date_label = ttk.Label(subscriptions_frame, text=subscription.get("end_date", ""))

                    # Store subscription widgets in a list
                    subscription_widgets.append((index_label, client_name_label, product_name_label, end_date_label))

                    # Grid the widgets
                    index_label.grid(row=i, column=0)
                    client_name_label.grid(row=i, column=1)
                    product_name_label.grid(row=i, column=2)
                    end_date_label.grid(row=i, column=3)

                self.subscription_widgets = subscription_widgets  # Save subscription widgets

            else:
                self.handle_error("Info", "No subscriptions available.")

        except requests.RequestException as e:
            self.handle_error("Error", f"Failed to retrieve subscriptions: {e}")

    def filter_subscriptions(self):
        search_query = self.search_var.get().lower()  # Access search_var with self
        for widget_set in self.subscription_widgets:
            index_label, client_name_label, product_name_label, end_date_label = widget_set
            # Get text from labels and check if it matches search query
            text = (index_label.cget("text") + " " +
                    client_name_label.cget("text") + " " +
                    product_name_label.cget("text") + " " +
                    end_date_label.cget("text")).lower()
            if search_query in text:
                # Show the widget if it matches the search query
                index_label.grid()
                client_name_label.grid()
                product_name_label.grid()
                end_date_label.grid()
            else:
                # Hide the widget if it doesn't match the search query
                index_label.grid_remove()
                client_name_label.grid_remove()
                product_name_label.grid_remove()
                end_date_label.grid_remove()

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
            self.handle_error("Error", str(e))

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
                    self.handle_error("Error", "Please enter a new end date.")
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
            self.handle_error("Error", str(e))

    def add_product(self):
        new_product = self.new_product_entry.get().strip()
        if new_product:
            try:
                # Check API status
                self.check_api_status()

                # Check if the product already exists
                if new_product in self.product_listbox.get(0, tk.END):
                    messagebox.showerror("Error", "Product already exists.")
                    return

                # Send request to add product
                api_url = f"http://{self.host}:{self.port}/add_product"
                response = requests.post(api_url, json={"product_name": new_product})
                response.raise_for_status()  # Raise an error for non-OK responses
                messagebox.showinfo("Success", "Product added successfully.")
                self.update_product_list()  # Update the product list after adding a new product
            except requests.RequestException as e:
                self.handle_error("Error", f"Failed to add product: {e}")
        else:
            self.handle_error("Error", "Please enter a product name.")

    def delete_product(self):
        selected_product_index = self.product_listbox.curselection()
        if selected_product_index:
            try:
                # Check API status
                self.check_api_status()

                # Get the selected product
                selected_product = self.product_listbox.get(selected_product_index)

                # Confirm deletion
                confirmation = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected_product}'?")
                if confirmation:
                    # Send request to delete product
                    api_url = f"http://{self.host}:{self.port}/delete_product"
                    response = requests.post(api_url, json={"product_name": selected_product})
                    response.raise_for_status()  # Raise an error for non-OK responses
                    messagebox.showinfo("Success", "Product deleted successfully.")
                    self.update_product_list()  # Update the product list after deleting
            except requests.RequestException as e:
                self.handle_error("Error", f"Failed to delete product: {e}")
        else:
            self.handle_error("Error", "Please select a product to delete.")

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
            if isinstance(e, requests.ConnectionError) or isinstance(e, requests.ConnectTimeout):
                self.handle_error("Error", "Failed to connect to the API. Please make sure the API is running.")
            else:
                self.handle_error("Error", f"Failed to retrieve products: {e}")

    def create_config_file(self, config_file_path):
        # Create a default config file
        config = configparser.ConfigParser()
        config["Form"] = {"host": "0.0.0.0", "port": "5002"}
        with open(config_file_path, "w") as configfile:
            config.write(configfile)

    def handle_error(self, title, message):
        messagebox.showerror(title, message)

def main():
    root = tk.Tk()
    app = SubscriptionFormApp(root)

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position for centering the window
    x = (screen_width - root.winfo_reqwidth()) // 2
    y = (screen_height - root.winfo_reqheight()) // 2

    # Set window position
    root.geometry("+{}+{}".format(x, y))

    root.mainloop()

if __name__ == "__main__":
    main()
