#!/usr/bin/env python

import subprocess
import os

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Run Subscription_API.py
    api_process = subprocess.Popen([os.path.join(script_dir, "Subscription_API.py")])

    # Run SubscriptionChecker.py
    checker_process = subprocess.Popen([os.path.join(script_dir, "SubscriptionChecker.py")])

    # Wait for both processes to finish
    api_process.wait()
    checker_process.wait()

if __name__ == "__main__":
    main()
