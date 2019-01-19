#!/usr/bin/env python3


from ansible.parsing.dataloader import DataLoader
from flask import Flask, request, abort, jsonify
import os
import yaml
from datetime import datetime, timedelta
import re


# inline configuration
APP_NAME = 'Ansible API'
CONFIGURATION_SOURCES = [
  './core/config.yaml',
  './default/config.yaml',
  './local/config.yaml'
]
CLIENT_AUTH_TIMEOUT = 24
#ANSIBLE_INVENTORY_PATH = '/etc/ansible/inventory/apple/dynamic'

# Set flask application name based off of configuration var
app = Flask(APP_NAME.lower().replace(' ', '_'))


@app.route(f"/{APP_NAME.lower().replace(' ', '_')}/add_host", methods=['GET', 'POST'])
def webhook():

  print(f'receiving <{request.method}> request')

  # If request is a get, whitelist client for 24 hours if token is valid
  if request.method == 'GET':
    authentication_token = request.args.get('authentication_token')
    if authentication_token == configuration['authentication_token']:
      authorized_clients[request.remote_addr] = datetime.now()
      return jsonify({'status':'successs'}), 200
    else:
      return jsonify({'status':'bad token'}), 401


  elif request.method == 'POST':
    client = request.remote_addr
    if client in authorized_clients:

      # If client token authentication has exceeded timeout, remove from
      # whitelist and deny request
      if datetime.now() - authorized_clients.get(client) > timedelta(hours=CLIENT_AUTH_TIMEOUT):
        authorized_clients.pop(client)
        return jsonify({'status':'authorization timeout'}), 401

      elif 'hostnames' not in request.json:
        return jsonify({'status':'missing hostnames parameter'}), 400

      else:
      
        if 'extra_vars' in request.json:
          extra_vars = request.json['extra_vars']
        else:
          extra_vars = ''

        if 'ansible_playbook_path' in request.json:
          ansible_playbook_path = request.json['ansible_playbook_path']
        else:
          ansible_playbook_path = '/etc/ansible/playbooks/test.yaml'

        if 'ansible_inventory_path' in request.json:
          ansible_inventory_path = request.json['ansible_inventory_path']
        elif 'ansible_inventory_path' in configuration:
          ansible_inventory_path = configuration['ansible_inventory_path']
        else:
          ansible_inventory_path = '/etc/ansible/inventory/test/dynamic'

        hostnames = request.json['hostnames']
        
        # TODO: 'is list' consideration should probably go into the add_host
        # function
        if isinstance(hostnames, list):
          for hostname in hostnames:
            print(f'Adding <{hostname}> to inventory')
            add_host_to_groups(hostname)
        else:
          print(f'Adding <{hostnames}> to inventory')
          add_host_to_groups(hostnames)

        # TODO: reintroduce extra vars
        os.system(f"ansible-playbook {ansible_playbook_path} -i {ansible_inventory_path} -l {hostnames}")


        return jsonify({'status':'success'}), 200

    # Client was not on whitelist  
    else:
      return jsonify({'status':'unauthorized'}), 401

  # Request was something other than GET or POST
  else:
    abort(400)


def add_host_to_groups(hostname):

  group_definitions = read_yaml('/etc/ansible/ansible_api/local/group_definitions.yaml')

  for group_definition in group_definitions:
    
    # Instantiate a variable to tell if a host was already seen in a file
    host_already_exists = False
    
    if re.compile(group_definition['regex']).match(hostname):

      hostfile = f"{configuration['ansible_inventory_path']}/{group_definition['name']}.ini"
      
      if not os.path.exists(hostfile):
        print(f'creating new inventory file <{hostfile}>')
        with open(hostfile, 'a+') as f:
          f.write(f"[{group_definition['name']}]\n")

      print(f'reading inventory file <{hostfile}>')
      with open(hostfile, 'r') as f:
        lines = f.readlines()
      for line in lines:
        if line.rstrip() == hostname:
          print(f'<{hostname}> found in <{hostfile}> -- skipping')
          host_already_exists = True
      
      if not host_already_exists:
        print(f'adding to inventory file <{hostfile}>')
        with open(hostfile, 'a+') as f:
          f.write(f'{hostname}\n')



def parse_inventory_definitions():
  pass

def merge_recursively(*args):
  """ Recursively merge any 2 or more dictionaries. """
  print(f'recurisve_merge invoked')

  # Placeholder object for return
  merged_data = {}
  print('placeholder merged dictionary created')

  # Iterate through all of the arguments and convert any troublesome ones into
  # empty dictionaries
  print('Insuring against bad arguments...')
  for data_source in args:
    print(f'Insuring <{data_source}>')

    # If data source is not a dictionary, convert it into an empty dictionary
    if not isinstance(data_source, dict):
      print('***** ERROR *****')
      print(f'<{data_source}> is not a dictionary! Converting to empty dictionary...')
      data_source = {}

    # If any keys are duplicated and either of them are dictionaries, then
    # merge the key recursively, otherwise just merge, overriding with last
    # loaded data
    for key, value in data_source.items():
      if (key in merged_data and
          (isinstance(value, dict) or
          isinstance(merged_dictionary[key], dict))):
        merged_data[key] = recursive_merge(merged_data[key], data_source[key])
      else:
        merged_data[key] = data_source[key]

  # Finally, return the merged dictionary
  return merged_data


def generate_authentication_token():
  """ Generate an authentication token """
  import binascii
  authentication_token = binascii.hexlify(os.urandom(24))
  return authentication_token.decode('utf-8')


def read_yaml(filepath):
  if not os.path.exists(filepath):
    print('***** ERROR *****')
    print(f'attempted to read non-existent file <{filepath}>!')
  else:

    # FIXME: not working
    #read_ansible_yaml(filepath)
    
    print('Ansible loading not working, using regular YAML loading')
    with open(filepath, 'r') as f:
      #yaml_contents = yaml.safe_load(f)
      yaml_contents = yaml.safe_load(f)
    return yaml_contents

def read_ansible_yaml(filepath):
  yaml_contents = yaml.load(filepath, Loader=ansible_loader)
  return yaml_contents


def create_ansible_loader():
  loader = DataLoader()
  return loader


def merge_configuration_data(data_sources):
  configuration = {}
  for data_source in data_sources:
    print(f'parsing configuration source <{data_source}>')
    configuration_data = read_yaml(data_source)
    configuration = merge_recursively(configuration_data)
  return configuration


def parse_configuration():
  configuration = merge_configuration_data(CONFIGURATION_SOURCES)

  if not 'authentication_token' in configuration.keys():
    print('Authentication token not detected in configuration data')
    configuration['authentication_token'] = generate_authentication_token()
    print(f"Generated authentication token: <{configuration['authentication_token']}>")

  #if not 'group_definitions' in configuration.keys():
  #  print('Group definitions not detected in configuration data')
  #  configuration['group_definitions'] = read_yaml('/etc/ansible/ansible_api/local/group_definitions.yaml')

  print(f'Configuration data: <{configuration}>')
  return configuration


# Run the app
if __name__ == '__main__':


  authorized_clients = {}

  # Create Ansible loader object, used to read YAML vault objects
  ansible_loader = create_ansible_loader()

  # Parse configuration sources
  #configuration = parse_configuration_data(CONFIGURATION_SOURCES)
  configuration = parse_configuration()

  # TODO: parameterize debug mode
  app.run(debug=True)
