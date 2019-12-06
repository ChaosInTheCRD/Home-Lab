# Home-Lab

**This Repository will outline all my plans, design considerations and processes that I used when redesigning my Lab Infrastructure**

## Specifications of Home Server

CPU: Intel i7 4770 (8) @ 3.90 GHz
Memory: 7849MiB
Storage: 120gb SATA SSD (Samsung EVO) & 6TB Seagate IronWolf

## Choice of Hypervisor
**Proxmox** is an open source platform for virtualisation based on Debian with a modified Ubuntu LTS kernel. After the last few years with Ubuntu running on my home server (unvirtualised), I figured this would be a familiar distro to work with, but with added capabilities for deploying more workloads, and a nice web interface for monitoring and config.

## What do I want to run?
So while it is not set in stone yet, I plan to run a bunch of stuff that should all share two key properties: 
a) they should be somewhat useful/relevant to mytechnical development, and 
b) they should have some real life benefit to the home-lab environment, rather than being tools that I use for the sake of it.

In terms of skills, the list of things I would like to develop are as follows:
1. Python, C, C++, Java programming
2. Bash Scripting
3. Use of automation tools (Puppet, Ansible, Chef etc.)
4. Slack Integration
5. VPN at the Proxmox level
6. ZFS
7. Bitnami Services
8. Hashicorp Vagrant
9. Snort
10. Stackify? **Needs more research**

Further to this, I have found a really cool ansible playbook created by Dave Stephens (https://github.com/davestephens/ansible-nas/blob/master/README.md). While I am not going to use it, there are countless container images that I wish deploy inside a VM:
1. Bazarr
2. Bitwarden
3. Calibre
4. Cloud Commander
5. Cloudflare DDNS
6. Duplicati
7. Firefly III
8. Glances
9. Grafana
10. Apache Guacamole
11. Heimdall
12. Jackett
13. Miniflux
14. Netdata
15. NextCloud
16. NZBget
17. Plex
18. Portainer
19. Radarr
20. Sonarr
21. Tautulli
22. Telegraf
23. The Lounge
24. TimeMachine
25. Traefik
26. Transmission with OpenVpn
27. WatchTower
