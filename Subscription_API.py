from flask import Flask, request, jsonify
import json
import configparser
import os
import sys

app = Flask(__name__)

print("RUNNING...API")

# Get the directory of the script
if getattr(sys, 'frozen', False):  # if the application is frozen (e.g. pyinstaller)
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Load configurations from config.ini
config = configparser.ConfigParser()
config_file_path = os.path.join(script_dir, "config.ini")
if os.path.exists(config_file_path):
    config.read(config_file_path)
    print("config.ini found")

# Get API configuration
api_host = config.get("API", "host", fallback="localhost")
api_port = config.getint("API", "port", fallback=5000)

# Load subscriptions
def load_subscriptions():
    try:
        with open(os.path.join(script_dir, "subscriptions.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save subscriptions
def save_subscriptions(subscriptions):
    with open(os.path.join(script_dir, "subscriptions.json"), "w") as file:
        json.dump(subscriptions, file)

# Load products
def load_products():
    try:
        with open(os.path.join(script_dir, "products.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save products
def save_products(products):
    with open(os.path.join(script_dir, "products.json"), "w") as file:
        json.dump(products, file)


# Generate a unique index for new subscriptions
def generate_index(subscriptions):
    indexes = [subscription.get("index", 0) for subscription in subscriptions]
    return max(indexes) + 1 if indexes else 1


@app.route('/add_subscription', methods=['POST'])
def add_subscription():
    try:
        data = request.json
        print("Received request data:", data)
        subscriptions = load_subscriptions()
        
        # Check if the product already exists
        if any(subscription["client_name"] == data["client_name"] and subscription["product_name"] == data["product_name"] for subscription in subscriptions):
            return jsonify({"error": "Subscription already exists."}), 400

        data["index"] = generate_index(subscriptions)
        subscriptions.append(data)
        save_subscriptions(subscriptions)
        print("Subscription added:", data)
        return jsonify({"message": "Subscription added successfully."}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/view_subscriptions', methods=['GET'])
def view_subscriptions():
    subscriptions = load_subscriptions()
    return jsonify(subscriptions), 200


@app.route('/delete_subscription', methods=['POST'])
def delete_subscription():
    index = request.json.get("index")
    subscriptions = load_subscriptions()
    index_exists = False
    for subscription in subscriptions:
        if subscription["index"] == index:
            subscriptions.remove(subscription)
            index_exists = True
            break
    if index_exists:
        save_subscriptions(subscriptions)
        return jsonify({"message": "Subscription deleted successfully."}), 200
    else:
        return jsonify({"message": "Invalid index."}), 400


@app.route('/renew_subscription', methods=['POST'])
def renew_subscription():
    index = request.json.get("index")
    new_end_date = request.json.get("new_end_date")
    subscriptions = load_subscriptions()
    for subscription in subscriptions:
        if subscription["index"] == index:
            subscription["end_date"] = new_end_date
            save_subscriptions(subscriptions)
            return jsonify({"message": "Subscription renewed successfully."}), 200
    return jsonify({"message": "Invalid index."}), 400


@app.route('/is_api_online', methods=['GET'])
def is_api_online():
    return jsonify({"status": "online"}), 200


@app.route('/get_products', methods=['GET'])
def get_products():
    products = load_products()
    return jsonify(products), 200


@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.json.get("product_name")
    if product_name:
        products = load_products()
        
        # Check if the product already exists
        if product_name in products:
            return jsonify({"error": "Product already exists."}), 400
        
        products.append(product_name)
        save_products(products)
        return jsonify({"message": "Product added successfully."}), 200
    else:
        return jsonify({"message": "Invalid product name."}), 400


@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_name = request.json.get("product_name")
    products = load_products()
    if product_name in products:
        products.remove(product_name)
        save_products(products)
        return jsonify({"message": "Product deleted successfully."}), 200
    else:
        return jsonify({"message": "Product does not exist."}), 400


if __name__ == '__main__':
    subscriptions_file_path = os.path.join(script_dir, "subscriptions.json")
    if not os.path.exists(subscriptions_file_path):
        with open(subscriptions_file_path, "w") as file:
            json.dump([], file)
    products_file_path = os.path.join(script_dir, "products.json")
    if not os.path.exists(products_file_path):
        with open(products_file_path, "w") as file:
            json.dump([], file)
    app.run(host=api_host, port=api_port, debug=True, use_reloader=False)  # Run the Flask app
