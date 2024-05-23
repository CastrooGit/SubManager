import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, date
import requests
import configparser
import os
import sys
from openpyxl import load_workbook


class SubscriptionFormApp:
    def __init__(self, master):
        self.master = master
        self.search_var = tk.StringVar()
        master.title("Subscription Form")

        if getattr(sys, 'frozen', False):
            self.script_dir = os.path.dirname(sys.executable)
        else:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))

        config_file_path = os.path.join(self.script_dir, "config.ini")

        if not os.path.exists(config_file_path):
            self.create_config_file(config_file_path)

        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

        self.host = self.config.get("Form", "host")
        self.port = self.config.getint("Form", "port")

        self.form_frame = ttk.Frame(master, padding="20")
        self.form_frame.grid(row=0, column=0, sticky="nsew")
        self.form_frame.columnconfigure(1, weight=1)

        ttk.Label(self.form_frame, text="Client Name:").grid(row=0, column=0, sticky="w")
        self.client_name_entry = ttk.Entry(self.form_frame)
        self.client_name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(self.form_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.end_date_entry = ttk.Entry(self.form_frame)
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(self.form_frame, text="License Key (optional):").grid(row=2, column=0, sticky="w")
        self.license_key_entry = ttk.Entry(self.form_frame)
        self.license_key_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(self.form_frame, text="Products:").grid(row=3, column=0, sticky="w")

        self.product_listbox = tk.Listbox(self.form_frame, selectmode=tk.SINGLE)
        self.product_listbox.grid(row=4, column=0, columnspan=2, padx=(0, 10), pady=5, sticky="nsew")
        self.product_listbox.bind("<<ListboxSelect>>", self.on_product_select)
        self.update_product_list()

        self.product_listbox.selection_clear(0, tk.END)

        ttk.Label(self.form_frame, text="New Product:").grid(row=5, column=0, sticky="w")
        self.new_product_entry = ttk.Entry(self.form_frame)
        self.new_product_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10))

        self.add_product_button = ttk.Button(self.form_frame, text="Add Product", command=self.add_product)
        self.add_product_button.grid(row=5, column=2, sticky="ew", padx=(0, 10))

        self.delete_product_button = ttk.Button(self.form_frame, text="Delete Product", command=self.delete_product)
        self.delete_product_button.grid(row=5, column=3, sticky="ew", padx=(0, 10))

        self.buttons_frame = ttk.Frame(master)
        self.buttons_frame.grid(row=1, column=0, pady=(10, 0))
        self.buttons_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.add_button = ttk.Button(self.buttons_frame, text="Add Subscription", command=self.add_subscription)
        self.add_button.grid(row=0, column=0, pady=5, padx=(0, 5), sticky="ew")

        self.view_button = ttk.Button(self.buttons_frame, text="View Subscriptions", command=self.view_subscriptions)
        self.view_button.grid(row=0, column=1, pady=5, padx=(0, 5), sticky="ew")

        self.delete_button = ttk.Button(self.buttons_frame, text="Delete Subscription", command=self.delete_subscription)
        self.delete_button.grid(row=0, column=2, pady=5, padx=(0, 5), sticky="ew")

        self.renew_button = ttk.Button(self.buttons_frame, text="Renew Subscription", command=self.renew_subscription)
        self.renew_button.grid(row=0, column=3, pady=5, padx=(0, 5), sticky="ew")

        self.import_button = ttk.Button(self.buttons_frame, text="Import from Excel", command=self.import_from_excel)
        self.import_button.grid(row=0, column=4, pady=5, padx=(0, 5), sticky="ew")

        self.check_api_status()

    def check_api_status(self):
        try:
            api_url = f"http://{self.host}:{self.port}/is_api_online"
            response = requests.get(api_url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.handle_error("Error", f"Failed to connect to the API: {e}")
            self.disable_buttons()

    def disable_buttons(self):
        self.add_button.config(state=tk.DISABLED)
        self.view_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.renew_button.config(state=tk.DISABLED)
        self.add_product_button.config(state=tk.DISABLED)
        self.delete_product_button.config(state=tk.DISABLED)
        self.import_button.config(state=tk.DISABLED)

    def add_subscription(self):
        client_name = self.client_name_entry.get().strip()
        selected_product = self.product_listbox.get(tk.ACTIVE)
        end_date_str = self.end_date_entry.get().strip()
        license_key = self.license_key_entry.get().strip() or None

        if not all([client_name, selected_product, end_date_str]):
            self.handle_error("Error", "Please fill in all fields except License Key.")
            return

        try:
            self.check_api_status()

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date < datetime.today().date():
                raise ValueError("End date cannot be in the past.")

            api_url = f"http://{self.host}:{self.port}/add_subscription"
            new_subscription = {
                "client_name": client_name,
                "product_name": selected_product,
                "end_date": end_date_str,
                "license_key": license_key
            }
            response = requests.post(api_url, json=new_subscription)
            response.raise_for_status()
            messagebox.showinfo("Success", "Subscription added successfully.")
        except (ValueError, requests.RequestException) as e:
            self.handle_error("Error", str(e))

    def view_subscriptions(self):
        try:
            self.check_api_status()

            api_url = f"http://{self.host}:{self.port}/view_subscriptions"
            response = requests.get(api_url)
            response.raise_for_status()

            subscriptions = response.json()

            if subscriptions:
                self.view_window = tk.Toplevel(self.master)
                self.view_window.title("View Subscriptions")

                screen_width = self.view_window.winfo_screenwidth()
                screen_height = self.view_window.winfo_screenheight()
                x = (screen_width - self.view_window.winfo_reqwidth()) // 2
                y = (screen_height - self.view_window.winfo_reqheight()) // 2
                self.view_window.geometry("+{}+{}".format(x, y))

                search_frame = ttk.Frame(self.view_window)
                search_frame.grid(row=0, column=0, columnspan=5, padx=10, pady=5, sticky="ew")

                search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
                search_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

                search_button = ttk.Button(search_frame, text="Search", command=self.filter_subscriptions)
                search_button.grid(row=0, column=1, padx=(5, 0))

                self.subscriptions_frame = ttk.Frame(self.view_window)
                self.subscriptions_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky="ew")

                ttk.Label(self.subscriptions_frame, text="Index", width=10, anchor='w').grid(row=0, column=0, sticky="w")
                ttk.Label(self.subscriptions_frame, text="Client Name", width=20, anchor='w').grid(row=0, column=1, sticky="w")
                ttk.Label(self.subscriptions_frame, text="Product Name", width=20, anchor='w').grid(row=0, column=2, sticky="w")
                ttk.Label(self.subscriptions_frame, text="End Date", width=15, anchor='w').grid(row=0, column=3, sticky="w")
                ttk.Label(self.subscriptions_frame, text="License Key", width=30, anchor='w').grid(row=0, column=4, sticky="w")

                self.subscription_labels = []

                for idx, subscription in enumerate(subscriptions):
                    client_name = subscription['client_name']
                    product_name = subscription['product_name']
                    end_date = subscription['end_date']
                    license_key = subscription['license_key'] if subscription['license_key'] else "N/A"

                    self.subscription_labels.append((
                        ttk.Label(self.subscriptions_frame, text=idx + 1, width=5, anchor='w'),
                        ttk.Label(self.subscriptions_frame, text=client_name, width=20, anchor='w'),
                        ttk.Label(self.subscriptions_frame, text=product_name, width=35, anchor='w'),
                        ttk.Label(self.subscriptions_frame, text=end_date, width=10, anchor='w'),
                        ttk.Label(self.subscriptions_frame, text=license_key, width=30, anchor='w')
                    ))

                    self.subscription_labels[-1][0].grid(row=idx + 1, column=0, sticky="w")
                    self.subscription_labels[-1][1].grid(row=idx + 1, column=1, sticky="w")
                    self.subscription_labels[-1][2].grid(row=idx + 1, column=2, sticky="w")
                    self.subscription_labels[-1][3].grid(row=idx + 1, column=3, sticky="w")
                    self.subscription_labels[-1][4].grid(row=idx + 1, column=4, sticky="w")

                self.subscriptions = subscriptions

        except requests.RequestException as e:
            self.handle_error("Error", str(e))



    def filter_subscriptions(self):
        search_term = self.search_var.get().lower()
        filtered_subscriptions = [
            (idx, subscription) for idx, subscription in enumerate(self.subscriptions)
            if (search_term in str(idx + 1) or
                search_term in subscription['client_name'].lower() or
                search_term in subscription['product_name'].lower())
        ]

        for widgets in self.subscription_labels:
            for widget in widgets:
                widget.destroy()

        self.subscription_labels = []

        for display_idx, (original_idx, subscription) in enumerate(filtered_subscriptions):
            client_name = subscription['client_name']
            product_name = subscription['product_name']
            end_date = subscription['end_date']
            license_key = subscription['license_key'] if subscription['license_key'] else "N/A"

            self.subscription_labels.append((
                ttk.Label(self.subscriptions_frame, text=display_idx + 1, width=10, anchor='w'),
                ttk.Label(self.subscriptions_frame, text=client_name, width=20, anchor='w'),
                ttk.Label(self.subscriptions_frame, text=product_name, width=20, anchor='w'),
                ttk.Label(self.subscriptions_frame, text=end_date, width=15, anchor='w'),
                ttk.Label(self.subscriptions_frame, text=license_key, width=30, anchor='w')
            ))

            self.subscription_labels[-1][0].grid(row=display_idx + 1, column=0, sticky="w")
            self.subscription_labels[-1][1].grid(row=display_idx + 1, column=1, sticky="w")
            self.subscription_labels[-1][2].grid(row=display_idx + 1, column=2, sticky="w")
            self.subscription_labels[-1][3].grid(row=display_idx + 1, column=3, sticky="w")
            self.subscription_labels[-1][4].grid(row=display_idx + 1, column=4, sticky="w")

        self.filtered_subscriptions = filtered_subscriptions

    def delete_subscription(self):
        try:
            self.check_api_status()

            index = simpledialog.askinteger("Delete Subscription", "Enter the index of the subscription to delete:")
            if index is None:
                return

            api_url = f"http://{self.host}:{self.port}/delete_subscription"
            response = requests.delete(api_url, json={"index": index - 1})
            response.raise_for_status()

            messagebox.showinfo("Success", "Subscription deleted successfully.")
        except requests.RequestException as e:
            self.handle_error("Error", str(e))

    def renew_subscription(self):
        try:
            self.check_api_status()

            index = simpledialog.askinteger("Renew Subscription", "Enter the index of the subscription to renew:")
            if index is None:
                return

            api_url = f"http://{self.host}:{self.port}/renew_subscription"
            response = requests.put(api_url, json={"index": index - 1})
            response.raise_for_status()

            messagebox.showinfo("Success", "Subscription renewed successfully.")
        except requests.RequestException as e:
            self.handle_error("Error", str(e))

    def update_product_list(self):
        try:
            self.check_api_status()

            api_url = f"http://{self.host}:{self.port}/get_products"
            response = requests.get(api_url)
            response.raise_for_status()

            products = response.json()
            self.product_listbox.delete(0, tk.END)
            for product in products:
                self.product_listbox.insert(tk.END, product)
        except requests.RequestException as e:
            self.handle_error("Error", str(e))

    def add_product(self):
        new_product = self.new_product_entry.get().strip()
        if new_product:
            try:
                self.check_api_status()

                api_url = f"http://{self.host}:{self.port}/add_product"
                response = requests.post(api_url, json={"product_name": new_product})
                response.raise_for_status()
                self.update_product_list()
                messagebox.showinfo("Success", "Product added successfully.")
            except requests.RequestException as e:
                self.handle_error("Error", str(e))

    def delete_product(self):
        selected_product = self.product_listbox.get(tk.ACTIVE)
        if selected_product:
            try:
                self.check_api_status()

                api_url = f"http://{self.host}:{self.port}/delete_product"
                response = requests.delete(api_url, json={"product_name": selected_product})
                response.raise_for_status()
                self.update_product_list()
                messagebox.showinfo("Success", "Product deleted successfully.")
            except requests.RequestException as e:
                self.handle_error("Error", str(e))

    def on_product_select(self, event):
        selected_product = self.product_listbox.get(tk.ACTIVE)
        self.new_product_entry.delete(0, tk.END)
        self.new_product_entry.insert(0, selected_product)

    def handle_error(self, title, message):
        messagebox.showerror(title, message)

    def create_config_file(self, config_file_path):
        config = configparser.ConfigParser()
        config['Form'] = {
            'host': 'localhost',
            'port': 5000
        }
        with open(config_file_path, 'w') as config_file:
            config.write(config_file)

    

    def import_from_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            workbook = load_workbook(filename=file_path)

            for sheet in workbook:
                for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
                    trimmed_row = row[:4]  # Only consider the first 4 columns

                    # Check if the row is entirely empty
                    if all(cell is None for cell in trimmed_row):
                        continue

                    if len(trimmed_row) != 4 or any(cell is None for cell in trimmed_row):
                        raise ValueError(f"Row does not have exactly 4 non-empty columns: {row}")

                    client_name, product_name, license_key, end_date = trimmed_row

                    # Check if the end date is in the future
                    if isinstance(end_date, datetime) and end_date <= datetime.now():
                        continue  # Skip this entry if end date is not in the future

                    end_date_str = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date

                    new_subscription = {
                        "client_name": client_name,
                        "product_name": product_name,
                        "end_date": end_date_str,
                        "license_key": license_key
                    }

                    api_url = f"http://{self.host}:{self.port}/add_subscription"
                    response = requests.post(api_url, json=new_subscription)
                    response.raise_for_status()

            messagebox.showinfo("Success", "Subscriptions imported successfully.")
        except ValueError as ve:
            self.handle_error("Error", f"Failed to import from Excel: {ve}")
        except Exception as e:
            self.handle_error("Error", f"Failed to import from Excel: {e}")




if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriptionFormApp(root)
    root.mainloop()
