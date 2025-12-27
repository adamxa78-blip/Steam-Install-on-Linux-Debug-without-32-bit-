import os
import platform
import subprocess
import sys
import shutil


def run(cmd, check=True):
    """Run a command (list form). Print and raise on error if check."""
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, check=check)


def has_command(cmd):
    return shutil.which(cmd) is not None


def read_os_release():
    data = {}
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k] = v.strip().strip('"')
    except Exception:
        pass
    return data


def ensure_root():
    if os.geteuid() != 0:
        print("This script must be run as root. Re-run with sudo:")
        print("  sudo " + " ".join(sys.argv))
        sys.exit(1)


def is_x86_64():
    arch = platform.machine()
    return arch in ("x86_64", "AMD64")


def apt_install(packages):
    run(["apt-get", "update"])
    run(["apt-get", "install", "-y"] + packages)


def setup_debian_like(os_id):
    # Ensure dpkg is present
    if not has_command("dpkg"):
        print("dpkg not found - this system may not be Debian-like.")
        sys.exit(1)

    # Ensure i386 architecture is enabled
    try:
        out = subprocess.check_output(["dpkg", "--print-foreign-architectures"], text=True)
    except subprocess.CalledProcessError:
        out = ""
    foreign = [l.strip() for l in out.splitlines() if l.strip()]
    if "i386" not in foreign:
        print("Adding i386 architecture (dpkg --add-architecture i386)")
        run(["dpkg", "--add-architecture", "i386"])
        run(["apt-get", "update"])
    else:
        print("i386 architecture already enabled.")

    # On Ubuntu-like, enable multiverse if possible
    if os_id in ("ubuntu", "linuxmint"):
        # install add-apt-repository if missing
        if not has_command("add-apt-repository"):
            print("Installing software-properties-common to manage repositories...")
            apt_install(["software-properties-common", "ca-certificates", "apt-transport-https"])
        try:
            # add multiverse and partner if not present
            print("Attempting to enable multiverse repository (Ubuntu/Mint).")
            run(["add-apt-repository", "-y", "multiverse"])
        except Exception as e:
            print("Could not run add-apt-repository: ", e)
            print("You may need to enable 'multiverse' manually in your sources.list.")

    # Ensure common 32-bit libraries to avoid "32-bit libraries missing" issues
    deb_32_pkgs = [
        "libc6:i386",
        "libstdc++6:i386",
        "libgl1:i386",
        "libgl1-mesa-dri:i386",
        "libgl1-mesa-glx:i386",
        "libx11-6:i386",
        "libxcb1:i386",
        "libxrandr2:i386",
        "libxinerama1:i386",
        "libxcursor1:i386",
        "libxi6:i386",
        "libxcomposite1:i386",
        "libasound2-plugins:i386",
    ]

    print("Installing common 32-bit compatibility libraries (may take a while)...")
    apt_install(deb_32_pkgs)

    # Try typical steam package names in order
    steam_candidates = ["steam", "steam-installer", "steam-launcher"]
    installed = False
    for pkg in steam_candidates:
        try:
            print(f"Attempting to install {pkg} ...")
            apt_install([pkg])
            installed = True
            break
        except subprocess.CalledProcessError:
            print(f"Failed to install {pkg}, trying next candidate...")

    if not installed:
        print("Couldn't install Steam via apt. You can try installing the .deb from Valve:")
        print("  https://store.steampowered.com/about/")
        print("Or install manually after ensuring multiverse and i386 libs are present.")
    else:
        print("Steam installation attempted. Run 'steam' as your user to finish setup.")


def setup_fedora_like():
    if not has_command("dnf"):
        print("dnf not found - this system may not be Fedora-like.")
        sys.exit(1)

    # Install common i686 libs
    fed_pkgs = [
        "glibc.i686",
        "libstdc++.i686",
        "libgcc.i686",
        "mesa-libGL.i686",
        "mesa-dri-drivers.i686",
        "libX11.i686",
        "libXrandr.i686",
        "libXinerama.i686",
        "libXcursor.i686",
        "libXi.i686",
        "libXcomposite.i686",
        "alsa-plugins-pulseaudio.i686",
    ]

    print("Installing common i686 libraries ...")
    run(["dnf", "install", "-y"] + fed_pkgs)

    # Ensure rpmfusion is available for Steam
    try:
        # Try installing rpmfusion repos (both free/nonfree)
        fedver = subprocess.check_output(["rpm", "-E", "%fedora"], text=True).strip()
        free = f"https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedver}.noarch.rpm"
        nonfree = f"https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedver}.noarch.rpm"
        print("Enabling RPM Fusion repositories for Steam (if not already enabled).")
        run(["dnf", "install", "-y", free, nonfree])
    except Exception as e:
        print("Could not enable RPM Fusion automatically:", e)
        print("You may need to enable RPM Fusion manually: https://rpmfusion.org/")

    # Install steam
    try:
        print("Installing steam via dnf ...")
        run(["dnf", "install", "-y", "steam"])
        print("Steam installation attempted. Run 'steam' as a normal user to complete setup.")
    except subprocess.CalledProcessError:
        print("Failed to install steam via dnf. Check repositories and try again.")


def setup_arch_like():
    if not has_command("pacman"):
        print("pacman not found - this system may not be Arch-like.")
        sys.exit(1)

    # Ensure multilib is enabled in /etc/pacman.conf
    multilib_enabled = False
    try:
        with open("/etc/pacman.conf", "r") as f:
            conf = f.read()
        if "[multilib]" in conf and "Include = /etc/pacman.d/mirrorlist" in conf:
            multilib_enabled = True
    except Exception:
        multilib_enabled = False

    if not multilib_enabled:
        print("The 'multilib' repository is not enabled in /etc/pacman.conf.")
        print("Please enable it (uncomment the [multilib] section and the Include line), then run:")
        print("  sudo pacman -Syu")
        sys.exit(1)

    print("Updating pacman and installing steam (this will install lib32 packages automatically)...")
    try:
        run(["pacman", "-Syu", "--noconfirm"])
        run(["pacman", "-S", "--noconfirm", "steam"])
        print("Steam installation attempted. Run 'steam' as a normal user to complete setup.")
    except subprocess.CalledProcessError:
        print("Failed to install steam via pacman.")


def main():
    ensure_root()

    if not is_x86_64():
        print("This script is intended for x86_64 systems. Steam for Linux requires x86_64 + 32-bit compatibility.")
        sys.exit(1)

    osrel = read_os_release()
    os_id = osrel.get("ID", "").lower()
    pretty = osrel.get("PRETTY_NAME", "")

    print(f"Detected system: {pretty} (ID={os_id})")
    # Decide package manager approach
    if has_command("apt-get") or os_id in ("debian", "ubuntu", "linuxmint"):
        setup_debian_like(os_id)
    elif has_command("dnf") or os_id in ("fedora", "rhel", "centos"):
        setup_fedora_like()
    elif has_command("pacman") or os_id in ("arch", "manjaro"):
        setup_arch_like()
    else:
        print("Unsupported or undetected distribution. The script currently supports Debian/Ubuntu, Fedora, and Arch.")
        print("You will need to enable 32-bit/multilib support and install steam manually:")
        print(" - Debian/Ubuntu: dpkg --add-architecture i386; apt update; install required :i386 libs; apt install steam")
        print(" - Fedora: install *.i686 packages (glibc.i686, libstdc++.i686, etc.) and 'dnf install steam' (enable rpmfusion)")
        sys.exit(1)


if __name__ == "__main__":
    main()
