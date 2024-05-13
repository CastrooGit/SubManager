# SubsCheck
Subscription Management System

The Subscription Management System is a Python-based application that allows users to manage subscriptions for various products and services.

Features

Add new subscriptions with client name, product name, and end date.
View existing subscriptions.
Delete subscriptions by their index.
Renew subscriptions with updated information.
API endpoints for easy integration with other systems.
Automatic email notifications for subscription expiry warnings and expiration.
Getting Started

Prerequisites
Python 3.x
Flask (pip install Flask)
smtplib (standard library)
json (standard library)
Installation
Clone the repository to your local machine:
bash
Copy code
git clone https://github.com/yourusername/subscription-management-system.git
Navigate to the project directory:
bash
Copy code
cd subscription-management-system
Install the required dependencies:
bash
Copy code
pip install -r requirements.txt
Usage
Start the API server:
bash
Copy code
python api.py
Start the subscription checker:
bash
Copy code
python checker.py
The API will be available at http://localhost:5000.

Use the API endpoints or the provided GUI to manage subscriptions.

API Endpoints
POST /add_subscription: Add a new subscription.

Example request body:
json
Copy code
{
    "client_name": "John Doe",
    "product_name": "Product X",
    "end_date": "2024-12-31"
}
GET /view_subscriptions: View existing subscriptions.

POST /delete_subscription: Delete a subscription by its index.

Example request body:
json
Copy code
{
    "index": 1
}
POST /renew_subscription: Renew a subscription with updated information.

Example request body:
json
Copy code
{
    "index": 1,
    "new_client_name": "Jane Smith",
    "new_product_name": "Product Y",
    "new_end_date": "2025-12-31"
}
GET /is_api_online: Check if the API server is online.

GET /get_next_index: Get the next available index for a new subscription.

Email Notifications
The subscription checker runs in the background and sends email notifications for subscription expiry warnings and expiration.
License

This project is licensed under the MIT License.

