import os
import json
import smtplib
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import configparser

class SubscriptionChecker:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email, subscriptions_file):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
        self.subscriptions_file = subscriptions_file
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.check_subscriptions).start()

    def stop(self):
        self.running = False

    def check_subscriptions(self):
        first_run = True
        while self.running:
            # Get the time until the next 10 o'clock
            now = datetime.now()
            next_check = datetime(now.year, now.month, now.day, 10, 0, 0)
            if now >= next_check:
                next_check += timedelta(days=1)  # Next day if already past 10 o'clock today
            sleep_time = (next_check - now).total_seconds()

            if first_run:
                print("SubscriptionChecker is running for the first time.")
                first_run = False

            time.sleep(sleep_time)  # Sleep until the next 10 o'clock
            self.load_subscriptions()
            self.send_email_notifications()

    def load_subscriptions(self):
        self.subscriptions = []
        with open(self.subscriptions_file, "r") as file:
            self.subscriptions = json.load(file)

    def send_email_notifications(self):
        today = datetime.today().date()
        for subscription in self.subscriptions:
            if isinstance(subscription, dict):
                end_date_str = subscription.get("end_date")
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    # Check if the subscription is due for a warning 45 days before expiration
                    if today + timedelta(days=45) == end_date:
                        self.send_warning_email(subscription)
                    elif end_date == today:
                        self.send_email(subscription)

    def send_warning_email(self, subscription):
        client_name = subscription["client_name"]
        product_name = subscription["product_name"]
        end_date = subscription["end_date"]
        subject = f"Subscription Expiry Warning: {client_name}"
        body = f"Dear User,\n\nYour subscription for {product_name} (client: {client_name}) is expiring in 45 days ({end_date}).\nPlease consider renewing it.\n\nRegards,\nYour Subscription Manager"

        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp_server:
                smtp_server.login(self.sender_email, self.sender_password)
                smtp_server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            print(f"Warning email sent for subscription: {client_name}")
        except Exception as e:
            print(f"Error sending warning email: {e}")

    def send_email(self, subscription):
        client_name = subscription["client_name"]
        product_name = subscription["product_name"]
        end_date = subscription["end_date"]
        subject = f"Subscription Expiry: {client_name}"
        body = f"Dear User,\n\nYour subscription for {product_name} (client: {client_name}) is expiring today ({end_date}).\n\nRegards,\nYour Subscription Manager"

        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp_server:
                smtp_server.login(self.sender_email, self.sender_password)
                smtp_server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            print(f"Email notification sent for subscription: {client_name}")
        except Exception as e:
            print(f"Error sending email: {e}")

def main():
    # Read SMTP settings from config.ini
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_file)

    smtp_server = config.get('SMTP', 'smtp_server')
    smtp_port = config.getint('SMTP', 'smtp_port')
    sender_email = config.get('SMTP', 'sender_email')
    sender_password = config.get('SMTP', 'sender_password')
    receiver_email = config.get('SMTP', 'receiver_email')
    subscriptions_file = os.path.join(os.path.dirname(__file__), 'subscriptions.json')

    checker = SubscriptionChecker(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subscriptions_file)
    checker.start()

    # Send a test email
    send_test_email(sender_email, sender_password, smtp_server, smtp_port, receiver_email)

def send_test_email(sender_email, sender_password, smtp_server, smtp_port, receiver_email):
    subject = "Test Email"
    body = "This is a test email sent on script boot up."

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, receiver_email, message.as_string())
        print("Test email sent successfully.")
    except Exception as e:
        print(f"Error sending test email: {e}")

if __name__ == "__main__":
    main()
