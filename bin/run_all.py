#!/usr/bin/env python

import subprocess
import os
import argparse

def run_all():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))
    project_dir = os.path.dirname(script_dir)

    # Run Subscription_API.py
    subprocess.Popen(["python3", os.path.join(project_dir, "Subscription_API.py")])

    # Run SubscriptionChecker.py
    subprocess.Popen(["python3", os.path.join(project_dir, "SubscriptionChecker.py")])

def main():
    parser = argparse.ArgumentParser(description='Run Subscription Manager')
    parser.add_argument('--run', action='store_true', help='Run Subscription Manager')
    args = parser.parse_args()

    if args.run:
        run_all()

if __name__ == "__main__":
    main()
