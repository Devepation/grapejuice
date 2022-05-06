title: Install Grapejuice on Ubuntu 18.04 and similar distributions
---
## Preamble

❓ If you didn't click on the guide for Ubuntu 18.04, but ended up on this page regardless, please do not panic! Ubuntu
18.04 is a distribution that is similar enough to other distributions in the Linux landscape. This guide is applicable
to the following distributions:

- Ubuntu 18.04 (Bionic Beaver)
- Zorin OS 15.2
- Linux Mint 19.3 (Tricia)

---

💻 All commands in this guide should be run in a terminal emulator using a regular user account that has access to `su`
or `sudo`. If you are running a fully fledged desktop environment, you can find a terminal emulator in your applications
menu.

---

⭐ Some commands do not produce any output. This usually means that the command ran successfully, so don't worry!

## Installing Grapejuice

1. First, we'll need to enable 32-bit support as 32-bit libraries are still required by Roblox: `sudo dpkg --add-architecture i386`
2. FAudio audio libraries are not supplied by the Ubuntu repositories, so we will have to install these manually. Run the following commands to install them:
    1. `wget https://download.opensuse.org/repositories/Emulators:/Wine:/Debian/xUbuntu_18.04/i386/libfaudio0_19.07-0~bionic_i386.deb -O /tmp/faudio_i386.deb`
    2. `wget https://download.opensuse.org/repositories/Emulators:/Wine:/Debian/xUbuntu_18.04/amd64/libfaudio0_19.07-0~bionic_amd64.deb -O /tmp/faudio_amd64.deb`
    3. `sudo apt install -y /tmp/faudio_i386.deb`
    4. `sudo apt install -y /tmp/faudio_amd64.deb`
3. You'll need to add the deadsnakes repository, as Grapejuice requires a newer version of Python:
    1. `sudo apt install -y software-properties-common`
    2. `sudo add-apt-repository ppa:deadsnakes/ppa`
4. Make sure your system is up to date with the following command: `sudo apt update && sudo apt upgrade -y`
5. The `curl` utility is required for the next step. Install it by running: `sudo apt install -y curl`
6. Install Grapejuice's keyring by running: `curl https://gitlab.com/brinkervii/grapejuice/-/raw/master/ci_scripts/signing_keys/public_key.gpg | sudo tee /usr/share/keyrings/grapejuice-archive-keyring.gpg > /dev/null`
7. To get access to the Grapejuice package, you'll need to add the repository. Do that using: `sudo tee /etc/apt/sources.list.d/grapejuice.list <<< 'deb [signed-by=/usr/share/keyrings/grapejuice-archive-keyring.gpg] https://brinkervii.gitlab.io/grapejuice/repositories/debian/ universal main' > /dev/null`
8. Since a new repository was added, you'll need to update your system so the package can be found: `sudo apt update`
9. Before installing Grapejuice, we'll need to install the Wine package: `sudo apt install wine`
10. Now, it's time to install the Grapejuice package: `sudo apt install -y grapejuice`
11. **One more step!** Before you can jump into the game, you'll need to install the patched wine version using [this guide](../Guides/Installing-Wine). If you don't do this, you'll encounter issues such as the game not starting, or the in-game mouse pointer not moving when it should.

## 🤔 Still having issues?

Even after installing Grapejuice and the patched wine version above, you may still have issues (examples: bad performance, Roblox not opening, etc). Usually, you can find the solutions here: [Troubleshooting page](../Troubleshooting)
