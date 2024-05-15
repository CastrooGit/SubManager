
```markdown
# Subscription Script

A simple subscription management system with an API and a checker.

---

## Features

- Add, view, delete, and renew subscriptions through a user-friendly GUI.
- API endpoints to perform CRUD operations on subscriptions.
- Email notifications for subscription renewals and expirations.

## Installation

### Prerequisites

- Python 3.x installed on your system.

### Clone the Repository

```bash
git clone https://github.com/CastrooGit/SubManager.git
cd SubscriptionScript
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the GUI Application

```bash
python SubscriptionForm.py
```

### Start the API

```bash
python Subscription_API.py
```

### Start the Subscription Checker

```bash
python SubscriptionChecker.py
```

## API Endpoints

- **GET /view_subscriptions**: View all subscriptions.
- **POST /add_subscription**: Add a new subscription.
  - Example request body:
    ```json
    {
        "client_name": "John Doe",
        "product_name": "Product A",
        "end_date": "2024-12-31"
    }
    ```
- **POST /delete_subscription**: Delete a subscription by index.
  - Example request body:
    ```json
    {
        "index": 1
    }
    ```
- **POST /renew_subscription**: Renew a subscription by index.
  - Example request body:
    ```json
    {
        "index": 1,
        "new_client_name": "Jane Doe",
        "new_product_name": "Product B",
        "new_end_date": "2025-12-31"
    }
    ```

## Email Notifications

- The Subscription Checker sends email notifications for renewals and expirations.
- Configure SMTP settings in `config.ini` to enable email notifications and setup server/api.

## License

This project is licensed under the [MIT License](LICENSE).
```
