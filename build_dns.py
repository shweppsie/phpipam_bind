#!/usr/bin/env python

import os
import phpipam
import json
import time
import sys
from string import Template
from subprocess import check_call

path = os.path.dirname(sys.argv[0])

from config import *

hosts = phpipam.get_hosts()

forward_output = open(os.path.join(path, 'templates/', forward_file)).read()
reverse_output = open(os.path.join(path, 'templates/', reverse_file)).read()

for host in hosts:
    forward_name = host['hostname'].split('.')[0]
    forward_output += "%s IN A %s\n" % (forward_name, host['ip'])

    reverse_ip = '.'.join(reversed(host['ip'].replace('192.168.', '').split('.')))
    reverse_name = host['hostname']
    if not reverse_name.endswith('.'):
        reverse_name += '.'
    reverse_output += "%s IN PTR %s\n" % (reverse_ip, reverse_name)

# create gen files if they don't exist as we need to compare against them
if not os.path.exists(os.path.join(bind_gen, forward_file)):
    open(os.path.join(bind_gen, forward_file), 'w').write("")
if not os.path.exists(os.path.join(bind_gen, reverse_file)):
    open(os.path.join(bind_gen, reverse_file), 'w').write("")

changed = False
if open(os.path.join(bind_gen, forward_file)).read() != forward_output:
    changed = True
    print "Updating forward"

    # write out the gen file
    open(os.path.join(bind_gen, forward_file), 'w').write(forward_output)

    # write out the actual file
    sub = {
        'serial': int(time.time()),
    }
    forward_output = Template(forward_output).safe_substitute(sub)
    print forward_output
    open(os.path.join(bind_dir, forward_file), 'w').write(forward_output)

if open(os.path.join(bind_gen, reverse_file)).read() != reverse_output:
    changed = True
    print "Updating reverse"

    # write out the gen file
    open(os.path.join(bind_gen, reverse_file), 'w').write(reverse_output)

    # write out the actual file
    sub = {
        'serial': int(time.time()),
    }
    reverse_output = Template(reverse_output).safe_substitute(sub)
    print reverse_output
    open(os.path.join(bind_dir, reverse_file), 'w').write(reverse_output)

if changed:
    check_call(['/usr/sbin/rndc', 'reload'])

