#!/usr/bin/env python3


import sys
import yaml
import re
import os


INVENTORY_ROOT = '/etc/ansible/inventory/apple/dynamic'
#REGEX_QUERIES_FILE = '/etc/ansible/scripts/inventory_generator_v2/regex_queries.yaml'
# FIXME
REGEX_QUERIES_FILE = '/etc/ansible/ansible_api/local/regex_queries.yaml'

GROUP_DEFINITIONS_FILE = '/etc/ansible/ansible_api/local/group_definitions.yaml'


def mergeRecursively(*args):
  merged_dictionary = {}
  dictionaries = args
  for dictionary in dictionaries:
    if not isinstance(dictionary, dict):
      dictionary = {}
    
    for key, value in dictionary.items():
      if (key in merged_dictionary and
          (isinstance(value, dict) or
          isinstance(merged_dictionary[key], dict))):

        merged_dictionary[key] = mergeRecursively(merged_dictionary[key], dictionary[key])

      else:
        
        merged_dictionary[key] = dictionary[key]

  return merged_dictionary        


# TODO: swap argv usage for argparse
# Parse hostname using argv
if len(sys.argv) < 2:
  print('Missing arguments!')
else:
  hostname = sys.argv[1]
  


# Create a list of regex queries to try against hostnames
#with open(REGEX_QUERIES_FILE, 'r') as f:
with open(GROUP_DEFINITIONS_FILE, 'r') as group_definitions_file:
  group_definitions = yaml.safe_load(group_definitions_file)
  group_definitions_file.close


#for query in queries:
for group_definition in group_definitions:
  host_exists = False
  if re.compile(group_definition['regex']).match(hostname):
    hostfile = '{}/{}.ini'.format(INVENTORY_ROOT, group_definition['name'])
    
    # Create the hostfile if it doesn't exist
    if not os.path.exists(hostfile):
      with open(hostfile, 'a+') as f:
        f.write('[{}]\n'.format(group_definition['name']))
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

    # Handle the group variable directory not existing
    # FIXME: what if path exists but its a file?
    if not os.path.exists(f'{INVENTORY_ROOT}/group_vars'):
      os.mkdir(f'{INVENTORY_ROOT}/group_vars')

    if 'vars' in group_definition:
      group_variables_file = f"{INVENTORY_ROOT}/group_vars/{group_definition['name']}.yaml"
      #with open(group_variable_file, 'r') as group_variable_file:
      #  lines = f.readlines()
      #for key, value in group_definitions.items():
      #  for line in lines:
      #    if line.rstrip() == 
      #print(f'group_variables file: {group_variables_file}')
      #with open(group_variables_file, 'r+') as f:
      #  group_variables = yaml.safe_load(f)
      #print(f'group_variables 1/2: {group_variables}')
      #group_variables = mergeRecursively(group_variables, group_definition['vars'])
      #print(f'group_variables 2/2: {group_variables}')
        #print(f'group_variables_file: {group_variables_file}')
      with open(group_variables_file, 'w+') as f:
        yaml.dump(group_definition['vars'], f, default_flow_style=False)
        

    ## Handle the group variable file
    ## If the group definition has a vars section, handle it
    #if 'vars' in group_definition:
    #  print("'vars' was in group_definition")
    #  group_variable_file = '{}/group_vars/{}.yaml'.format(INVENTORY_ROOT, group_definition['name'])
    #  # If file doesn't exist, create and add all content
    #  #if not os.path.exists(group_variable_file):
    #  with open(group_variable_file, 'w') as group_variable_file:
    #    #group_variable_file.write(f"[{group_definition['name']}]\n")
    #    ## For each variable in group variables, add the key/value
    #    #for key, value in group_definition['vars'].items():
    #    #  group_variable_file.write(f'{key}: {value}')
    #    yaml.dump(group_definition['vars'], group_variable_file, default_flow_style=False)
