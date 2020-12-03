# Get Homelab Data
This is a monitoring / collection tool for my homelab.
The current Stack is python, influxDB and Grafana running on a raspberryPI.
Docker containers are used to run influxDB and Grafana. The python application
is set up as a systemd service.

## Python
This is used to collect metrics from VM's, PI's, Proxmox (Hypervisor) and general network Health.

Libraries:
- subprocess
- requests
- nornir
- spur
- re 
- influxDB-Client


## Future expansion:
- temp, ram and cpu usage expanded
- Mikrotik SwOS data
- ZFS Stats
