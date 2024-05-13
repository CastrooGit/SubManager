import requests
import json
import os
import subprocess

def fetch_latest_release(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def download_and_replace_executable(repo_owner, repo_name, download_url):
    # Download the release package
    response = requests.get(download_url)
    if response.status_code == 200:
        # Save the downloaded zip file
        with open("latest_release.zip", "wb") as file:
            file.write(response.content)
        
        # Unzip the package
        os.system("unzip -o latest_release.zip")

        # Replace the old executable with the new one
        os.replace("dist/your_script", "your_script")

        # Clean up
        os.remove("latest_release.zip")
        os.system("rm -r dist")

def check_for_updates(repo_owner, repo_name, current_version):
    latest_release = fetch_latest_release(repo_owner, repo_name)
    if latest_release:
        latest_version = latest_release['tag_name']
        if latest_version != current_version:
            print("A new version is available. Updating...")
            assets = latest_release['assets']
            for asset in assets:
                if asset['name'].endswith(".zip"):
                    download_url = asset['browser_download_url']
                    download_and_replace_executable(repo_owner, repo_name, download_url)
            print("Update complete.")
        else:
            print("You are already using the latest version.")
    else:
        print("Failed to check for updates.")

def main():
    # GitHub repository information
    repo_owner = "your_username"
    repo_name = "your_repository"

    # Current version of the executable
    current_version = "1.0"  # Update with your actual version

    # Check for updates
    check_for_updates(repo_owner, repo_name, current_version)

    # Run the application
    subprocess.run(["./your_script"])  # Change the command if needed

if __name__ == "__main__":
    main()
