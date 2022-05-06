title: Install Grapejuice on Debian 10 and similar
---
## Preamble

❓ If you didn't click on the guide for Debian, but ended up on this page regardless, please do not panic! Debian is a
distribution that is the base for many other distributions in the Linux landscape. This guide is applicable to the
following distributions:

- Debian 10 (buster)
- Debian 11 (bullseye)
- Ubuntu 21.10 (Impish Indri)
- Ubuntu 21.04 (Hirsute Hippo)
- Ubuntu 20.04 (Focal Fossa)
- LMDE 4 (Debbie)
- Linux Mint 20 (Ulyana)
- Zorin OS 16
- Chrome OS

---

❗ This guide assumes that you've properly set up `sudo` on your Debian system.

Don't know what any of that means? If you've installed Ubuntu, Linux Mint, or selected a desktop environment in the
Debian installer, don't worry about this.

---

💻 All commands in this guide should be run in a terminal emulator using a regular user account that has access to `su`
or `sudo`. If you are running a fully fledged desktop environment, you can find a terminal emulator in your applications
menu.

## Installing Grapejuice

1. First, we'll need to enable 32-bit support as 32-bit libraries are still required by Roblox: `sudo dpkg --add-architecture i386`
2. We have to make sure that all repositories and locally installed packages are up to date. Run the following command in a terminal: `sudo apt update && sudo apt upgrade -y`
3. The `curl` utility is required for the following step. Run the following command in a terminal: `sudo apt install -y curl`
4. Install Grapejuice's keyring by running: `curl https://gitlab.com/brinkervii/grapejuice/-/raw/master/ci_scripts/signing_keys/public_key.gpg | sudo tee /usr/share/keyrings/grapejuice-archive-keyring.gpg > /dev/null`
5. To get access to the Grapejuice package, you'll need to add the repository. Do that using: `sudo tee /etc/apt/sources.list.d/grapejuice.list <<< 'deb [signed-by=/usr/share/keyrings/grapejuice-archive-keyring.gpg] https://brinkervii.gitlab.io/grapejuice/repositories/debian/ universal main' > /dev/null`
6. Since a new repository was added, you'll need to update your system so the package can be found: `sudo apt update`
7. Before installing Grapejuice, we'll need to install the Wine package: `sudo apt install wine`
8. Now, it's time to install the Grapejuice package: `sudo apt install -y grapejuice`
9. **One more step!** Before you can jump into the game, you'll need to install the patched wine version using [this guide](../Guides/Installing-Wine). If you don't do this, you'll encounter issues such as the game not starting, or the in-game mouse pointer not moving when it should.

## 🤔 Still having issues?

Even after installing Grapejuice and the patched wine version above, you may still have issues (examples: bad performance, Roblox not opening, etc). Usually, you can find the solutions here: [Troubleshooting page](../Troubleshooting)
