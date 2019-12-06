# Initial Setup Diary

After using [Rufus](https://github.com/pbatard/rufus/releases/download/v3.8/rufus-3.8.exe) on Windows 10 to create the Proxmox ISO (using dd mode), I installed Proxmox onto the system.


After rebooting, I ssh'd into Proxmox and inserted the following into the /etc/apt/sources.list file:
```
deb http://ftp.debian.org/debian buster main contrib
deb http://ftp.debian.org/debian buster-updates main contrib

# PVE pve-no-subscription repository provided by proxmox.com,
# NOT recommended for production use
deb http://download.proxmox.com/debian/pve buster pve-no-subscription

# security updates
deb http://security.debian.org buster/updates main contrib
```
I then rebooted again, and entered the web interface (https)

## Creating Rancher OS VM

If I'm honest this was a bit of a pain and took a little bit of time as it was a bit of a weird install compared to your standard Linux distribution. I wanted Rancher OS because it seemed to be the most lightweight, and as the OS front end is completely made up of docker containers, I felt I would learn more than if i'd just installed docker on Ubuntu.

The specifications of the VM deployed were 1 vCPU and 3gb RAM. this left me with 7 vCPU and 13gb RAM to allocate to other machines. However, I do expect that once everything has been configured this will increase considerably as this VM will be running the majority of my workloads.

