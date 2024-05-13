from flask import Flask, request, jsonify
import json
import configparser

app = Flask(__name__)

# Load configurations from config.ini
config = configparser.ConfigParser()
config_file_path = "config.ini"
config.read(config_file_path)

# Get host and port from config.ini
host = config.get("API", "host")
port = config.getint("API", "port")

# Load subscriptions
def load_subscriptions():
    with open("subscriptions.json", "r") as file:
        return json.load(file)

# Save subscriptions
def save_subscriptions(subscriptions):
    with open("subscriptions.json", "w") as file:
        json.dump(subscriptions, file)

@app.route('/add_subscription', methods=['POST'])
def add_subscription():
    data = request.json
    subscriptions = load_subscriptions()
    subscriptions.append(data)
    save_subscriptions(subscriptions)
    return jsonify({"message": "Subscription added successfully."}), 200

@app.route('/view_subscriptions', methods=['GET'])
def view_subscriptions():
    subscriptions = load_subscriptions()
    return jsonify(subscriptions), 200

@app.route('/delete_subscription', methods=['POST'])
def delete_subscription():
    index = request.json.get("index")
    subscriptions = load_subscriptions()
    if 0 < index <= len(subscriptions):
        del subscriptions[index - 1]
        save_subscriptions(subscriptions)
        return jsonify({"message": "Subscription deleted successfully."}), 200
    else:
        return jsonify({"message": "Invalid index."}), 400

@app.route('/renew_subscription', methods=['POST'])
def renew_subscription():
    index = request.json.get("index")
    subscriptions = load_subscriptions()
    if 0 < index <= len(subscriptions):
        subscription = subscriptions[index - 1]
        # Ask for new details
        new_client_name = request.json.get("new_client_name")
        new_product_name = request.json.get("new_product_name")
        new_end_date = request.json.get("new_end_date")

        subscription["client_name"] = new_client_name
        subscription["product_name"] = new_product_name
        subscription["end_date"] = new_end_date

        save_subscriptions(subscriptions)
        return jsonify({"message": "Subscription renewed successfully."}), 200
    else:
        return jsonify({"message": "Invalid index."}), 400

if __name__ == '__main__':
    app.run(host=host, port=port)