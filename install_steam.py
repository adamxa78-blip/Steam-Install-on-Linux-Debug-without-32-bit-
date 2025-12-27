#!/usr/bin/env python3
import subprocess
import os

def install_steam():
    print("--- Starting Steam amd64 Installation ---")
    
    # 1. Download the latest Steam .deb package
    deb_url = "https://repo.steampowered.com/steam/archive/stable/steam_latest.deb"
    print(f"Downloading from: {deb_url}")
    subprocess.run(["wget", "-O", "steam_latest.deb", deb_url], check=True)
    
    # 2. Install the .deb package using apt (handles dependencies)
    # This requires sudo permissions
    print("Installing Steam... (You may be prompted for your password)")
    try:
        # Using './' tells apt to look for a local file rather than a repository package
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "./steam_latest.deb"], check=True)
        print("\nSUCCESS: Steam has been installed.")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Installation failed. {e}")
    finally:
        # 3. Clean up the downloaded file
        if os.path.exists("steam_latest.deb"):
            os.remove("steam_latest.deb")

if __name__ == "__main__":
    install_steam()
