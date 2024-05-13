import os
import subprocess
import sys

def main():
    # Get the directory where the script is located
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the necessary files
    config_file = os.path.join(base_path, "..", "config.ini")  # Adjust the relative path
    subscriptions_file = os.path.join(base_path, "..", "subscriptions.json")  # Adjust the relative path
    api_script = os.path.join(base_path, "Subscription_API.py")
    checker_script = os.path.join(base_path, "SubscriptionChecker.py")
    update_checker_script = os.path.join(base_path, "update_checker.py")

    # Execute Subscription_API.py
    subprocess.run([sys.executable, api_script])

    # Execute SubscriptionChecker.py
    subprocess.run([sys.executable, checker_script])

    # Execute update_checker.py
    subprocess.run([sys.executable, update_checker_script])

if __name__ == "__main__":
    main()
