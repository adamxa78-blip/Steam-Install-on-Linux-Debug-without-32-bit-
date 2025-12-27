#!/usr/bin/env python3
import os
import subprocess
import sys

def install_steam():
    # 1. Official Steam download link for 64-bit Debian/Ubuntu
    steam_url = "https://steamcdn-a.akamaihd.net/client/installer/steam.deb"
    deb_name = "steam_latest.deb"

    print("--- Starting Steam Installation (2025) ---")
    
    # 2. Download the package
    try:
        print(f"Downloading Steam from {steam_url}...")
        subprocess.run(["wget", "-O", deb_name, steam_url], check=True)
    except Exception as e:
        print(f"Error downloading: {e}")
        return

    # 3. Install the package using apt (handles dependencies automatically)
    try:
        print("Installing Steam. This requires administrative privileges...")
        # Use 'sudo apt install ./' to ensure local .deb dependency resolution
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", f"./{deb_name}", "-y"], check=True)
        print("Installation complete!")
    except subprocess.CalledProcessError:
        print("Installation failed. Check your permissions or internet connection.")
    finally:
        # Clean up the downloaded file
        if os.path.exists(deb_name):
            os.remove(deb_name)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Please run this script with sudo or through the C++ installer.")
        # Re-run itself with sudo if necessary
        # subprocess.run(["sudo", "python3", __file__])
    install_steam()
