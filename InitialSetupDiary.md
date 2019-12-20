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

-- Update: I did not originally understand what it was I was doing, but I have now understood the point of the cloud-config.yml for the RancherOS setup, and setup a config to easily ssh to my rancher OS node. What I was not understanding was that upon install, the passwords set in live environment don't persist (obviously), and the correct configuration of the ssh keys and the IP address for the machine was criticial.

## *Side Note* ##
After a bit of thought I figured it would be best to have some sort of authorisation server sat in front of the nginx/traefik proxy that requires 2fa for access to services. This will give me peace of mind that I am at least trying to not give everyone relatively easy access to my stuff :)

A bit of reading led me to [Authelia](https://github.com/clems4ever/authelia). Seems to be a good project, and I can just setup Google Authenticator for 2FA. Cool task, something I've never done before.


## Lets Get Tunelling: Setup of OpenVPN Server ##
Now that I had successfully setup ROS, and was able to get access over the local network; the next step was to provide myself with a means of access to all the services running on the network no matter where I was. Traditionally, I had achieved this through reverse proxies and simple port forwards, but I felt that this was an opportunity to do something more thorough and secure (AKA exciting). I want to design this server to be secure, but also want it to give me ultimate control when needed. This is what brings me to OpenVPN!

I had read articles about people running raspberry pi's as OpenVPN servers, and have friends with machines that act as gateways for the same purpose of a secure but thorough access point to the local network. I want this server to be containerised... so a docker image with this functionality was the first thing I needed to find. [A medium article](https://medium.com/@gurayy/set-up-a-vpn-server-with-docker-in-5-minutes-a66184882c45) written by Guray Yildirim outlines a '5 minute' guide to setting up a VPN server with Docker using [Kyle Mannas Docker OpenVPN image](https://github.com/kylemanna/docker-openvpn.git). Well... what I can tell you is that it certainly did not take me 5 minutes, however this was not through the fault of the guide, and more my incompetence.

After realising that generating a config specifying the local ip for the Rancher VM was not going to work (of course the public IP is required), and also that there was no way the router could understand the request without declaring a port forward for the relevant UDP port, I was able to use Tunnelblick on MacOS to get a secure tunnel home! In fact, I sit typing write now on the A1 up to Scotland, and plan on pushing this git change via my newly formed OVPN container :)
