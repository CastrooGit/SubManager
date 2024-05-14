import os
import subprocess
import sys

def main():
    print("RUNNING...")
    # Get the directory where the script is located
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the necessary files
    config_file = os.path.join(base_path, "..", "config.ini")  # Adjust the relative path
    subscriptions_file = os.path.join(base_path, "..", "subscriptions.json")  # Adjust the relative path
    api_script = os.path.join(base_path, "Subscription_API.py")
    checker_script = os.path.join(base_path, "SubscriptionChecker.py")

    # Execute Subscription_API.py
    print("Executing Subscription_API.py...")
    try:
        subprocess.run([sys.executable, api_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {api_script}: {e}")

    print("Executing SubscriptionChecker.py...")
    # Execute SubscriptionChecker.py
    try:
        subprocess.run([sys.executable, checker_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {checker_script}: {e}")

    
if __name__ == "__main__":
    main()
