#!/usr/bin/env python3


import sys
import yaml
import re
import os


INVENTORY_ROOT = '/etc/ansible/inventory/apple/dynamic'
REGEX_QUERIES_FILE = '/etc/ansible/scripts/inventory_generator_v2/regex_queries.yaml'


# TODO: swap argv usage for argparse
# Parse hostname using argv
if len(sys.argv) < 2:
  print('Missing arguments!')
else:
  hostname = sys.argv[1]
  


# Create a list of regex queries to try against hostnames
with open(REGEX_QUERIES_FILE, 'r') as f:
  queries = yaml.safe_load(f)
  f.close


for query in queries:
  host_exists = False
  if re.compile(query['regex']).match(hostname):
    hostfile = '{}/{}.ini'.format(INVENTORY_ROOT, query['name'])
    
    # Create the hostfile if it doesn't exist
    if not os.path.exists(hostfile):
      with open(hostfile, 'a+') as f:
        f.write('[{}]\n'.format(query['name']))
        f.close
    # If it does exist, make sure the hostname isn't already present
    else:
      with open(hostfile, 'r') as f:
        existing_lines = f.readlines()
        f.close()
      for line in existing_lines:
        #print('Considering line/hostname: {}/{}'.format(line.rstrip(), hostname))
        #if str(hostname) in line:
        if line.rstrip() == hostname:
          #print('host already exists in file, skipping')
          host_exists = True
    # As long as the hostname wasn't already present, add the hostname
    if not host_exists:
      with open(hostfile, 'a+') as f:
        f.write('{}\n'.format(hostname)) 
        f.close()
