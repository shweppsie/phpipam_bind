# phpIPAM bind zonefile generator

This script fetches hosts from phpipam and adds them to your zonefiles and then reloads bind if changes have occured.

## Instuctions for use

1. Clone the repo to you machine.
1. Copy config.py.dist to config.py and update the config values to suit.
1. In templates put your zone files (minus the hosts the script adds from phpipam) but replace the serial with `{serial}`.
1. Add build_dns.py to you crontab.

Licence does not apply to libraries I have include: phpipam.py and rijndael.py (see headers on the individual files).
