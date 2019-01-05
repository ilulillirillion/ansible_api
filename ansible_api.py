#!/usr/bin/env python3


import os
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify


# Formal app name used in various places
APP_NAME = 'Ansible API'

# Token used for authentication
AUTHENTICATION_TOKEN = os.getenv('{}_AUTHENTICATION_TOKEN'.format(APP_NAME.upper().replace(' ', '_')))

# Number of hours for a client to remain on authentication whitelist once
# successfully authenticated
CLIENT_AUTH_TIMEOUT = 24

# Location of the Ansible hosts file
INVENTORY_HOSTS_FILE = os.getenv('{}_INVENTORY_HOSTS_FILE'.format(APP_NAME.upper().replace(' ', '_')))

# Location for Ansible inventory path
ANSIBLE_INVENTORY_PATH = os.getenv('{}_ANSIBLE_INVENTORY_PATH'.format(APP_NAME.upper().replace(' ', '_')))

# Location of playbook for Ansible to run
ANSIBLE_PLAYBOOK_PATH = os.getenv('{}_ANSIBLE_PLAYBOOK_PATH'.format(APP_NAME.upper().replace(' ', '_')))

# Script to use when adding hosts
ADD_HOST_SCRIPT = '/etc/ansible/scripts/inventory_generator_v2/add_host.py'


# Set the name of the 
app = Flask(APP_NAME.lower().replace(' ', '_'))

# Initialized list of authorized clients
authorized_clients = {}


# Generate a temporary token, if one is not provided
def generateAuthenticationToken():
  import binascii
  authentication_token = binascii.hexlify(os.urandom(24))
  return authentication_token.decode('utf-8')


@app.route('/{}'.format(APP_NAME.lower().replace(' ', '_')), methods=['GET', 'POST'])
def webhook():
  if request.method == 'GET':
    authentication_token = request.args.get('authentication_token')
    if authentication_token == AUTHENTICATION_TOKEN:
      authorized_clients[request.remote_addr] = datetime.now()
      return jsonify({'status':'success'}), 200
    else:
      return jsonify({'status':'bad token'}), 401

  elif request.method == 'POST':
    client = request.remote_addr
    if client in authorized_clients:
      if datetime.now() - authorized_clients.get(client) > timedelta(hours=CLIENT_AUTH_TIMEOUT):
        authorized_clients.pop(client)
        return jsonify({'status':'authorization timeout'}), 401
      else:
        os.system('python3 {} {}'.format(ADD_HOST_SCRIPT, request.json['hostname']))
        # TODO: will this work without passing extra-vars?
        os.system('ansible-playbook {} -i {}  -l {} --extra-vars "{}"'.format(ANSIBLE_PLAYBOOK_PATH, ANSIBLE_INVENTORY_PATH, request.json['hostname'], request.json['extra_vars']))
        return jsonify({'status':'success'}), 200
    else:
      return jsonify({'status':'not authorized'}), 401

  else:
    abort(400)

if __name__ == '__main__':
  if AUTHENTICATION_TOKEN is None:
    print('{}_AUTHENTICATION_TOKEN has not been set in the environment.\nGenerating random token...'.format(APP_NAME.upper().replace(' ', '_')))
    token = generateAuthenticationToken()
    print('Token: %s' % token)
    AUTHENTICATION_TOKEN = token
  if ANSIBLE_PLAYBOOK_PATH is None:
    raise Exception('ANSIBLE_PLAYBOOK_PATH is not defined!')
  if ANSIBLE_INVENTORY_PATH is None:
    raise Exception('ANSIBLE_INVENTORY_PATH is not defined!')
  app.run()
