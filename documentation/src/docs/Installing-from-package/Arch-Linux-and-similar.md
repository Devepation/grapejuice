title: Install Grapejuice on Arch Linux and similar distributions
---

## Preamble

:question: If you didn't click on the guide for Arch Linux, but ended up on this page regardless, please do not panic!
Arch Linux is a distribution that is the base for other distributions in the Linux landscape. This guide is applicable
to the following distributions:

- Arch Linux
- Manjaro Linux
- SteamOS 3.0

---

:computer: Grapejuice assumes your desktop is configured properly.

---

## SteamOS 3.0

Before you begin, if you are using SteamOS 3.0, you will need to run `sudo steamos-readonly disable` once you have done
that, you may continue.

## Installing Grapejuice

1. Enable the [multilib repository](https://wiki.archlinux.org/title/Official_repositories#multilib).
2. Get an [AUR helper](https://wiki.archlinux.org/title/AUR_helpers) or
   [learn how to install packages from the AUR manually](https://wiki.archlinux.org/title/Arch_User_Repository).
3. Install the `base-devel` package group with `sudo pacman -S base-devel`.
4. Install the `wine` package with `sudo pacman -S wine`.
5. Install [grapejuice-git](https://aur.archlinux.org/packages/grapejuice-git/) through an AUR helper or manually.
6. Open Grapejuice (via terminal: grapejuice-gui)
7. Get the patched wine version using [this guide](../Guides/Installing-Wine). If you don't do this, you'll encounter issues with the in-game mouse pointer or experience crashes.

Once Grapejuice has been installed, you can take a look at the sections below.

## Installing dependencies for audio

If you're using Pipewire (check if the `pipewire` process is running), follow
[these instructions](https://wiki.archlinux.org/title/PipeWire#PulseAudio_clients).

If you're not using Pipewire, you don't need to do anything.

## 🤔 Still having issues?

Even after installing Grapejuice and the patched wine version above, you may still have issues (examples: bad
performance, Roblox not opening, etc). Usually, you can find the solutions
here: [Troubleshooting page](../Troubleshooting)
