#!/usr/bin/env python3


import collections
import os
import sys
# ^ Required for rudimentary logging, can possibly remove later
import logging
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify


# Temporary variable
DEBUG_MODE = True

# FIXME: deprecated -- remove -- do not use
# Filepath for configuration file
CONFIGURATION_FILE_PATH = 'config.yaml'

# Core configs
CORE_CONFIGURATION_FILE_PATH = 'core/config.yaml'

# Default configs
DEFAULT_CONFIGURATION_FILE_PATH = 'default/config.yaml'

# Local configs
LOCAL_CONFIGURATION_FILE_PATH = 'local/config.yaml'

# Formal app name used in various places
APP_NAME = 'Ansible API'

# Token used for authentication
AUTHENTICATION_TOKEN = os.getenv('{}_AUTHENTICATION_TOKEN'.format(APP_NAME.upper().replace(' ', '_')))

# Number of hours for a client to remain on authentication whitelist once
# successfully authenticated
CLIENT_AUTH_TIMEOUT = 24

# Location of the Ansible hosts file
#INVENTORY_HOSTS_FILE = os.getenv('{}_INVENTORY_HOSTS_FILE'.format(APP_NAME.upper().replace(' ', '_')))

# Location for Ansible inventory path
#ANSIBLE_INVENTORY_PATH = os.getenv('{}_ANSIBLE_INVENTORY_PATH'.format(APP_NAME.upper().replace(' ', '_')))

# Location of playbook for Ansible to run
#ANSIBLE_PLAYBOOK_PATH = os.getenv('{}_ANSIBLE_PLAYBOOK_PATH'.format(APP_NAME.upper().replace(' ', '_')))

# Script to use when adding hosts
#ADD_HOST_SCRIPT = '/etc/ansible/scripts/inventory_generator_v2/add_host.py'
ADD_HOST_SCRIPT = '/etc/ansible/ansible_api/core/scripts/add_host.py'


# Set the name of the 
app = Flask(APP_NAME.lower().replace(' ', '_'))

# Initialized list of authorized clients
authorized_clients = {}


class DummyObject(object):
  def __getattr__(self, name):
    return lambda *x: None


# FIXME: deprecated -- remove -- do not use
# Generate a logger object
def setupLogger__():
  if configuration['simple_logging']:
    setupSimpleLogger()
  else:
    setupAdvancedLogger()  

  logger = logging.getLogger()


# FIXME: deprecated -- remove -- do not use
#def setupSimpleLogger__():

  ## Sanity-check variables
  # simple_logging_logfile
#  simple_logging_logfile = str(configuration['simple_logging_logfile'])
#  if simple_logging_logfile is None:
#    simple_logging_logfile = 'ansible_api.log'
#  # simple_logging_formatting
#  simple_logging_formatting = str(configuration['simple_logging_formatting'])
#  if simple_logging_formatting is None:
#    simple_logging_formatting = ''
#  # simple_logging_level
#  simple_logging_level = configuration['simple_logging_level']
#  if simple_logging_level is None:
#    simple_logging_level = 'DEBUG'
#  if isinstance(simple_logging_level, str):
#    simple_logging_level = logging.getLevelName(simple_logging_level.upper())
#
#  logger = logging.getLogger()
#  
#  # Set stream using getattr to avoid finding correct value
#  stream_handler = logging.StreamHandler(getattr(sys, 'stdout'))
#  # Set file handler using raw string var
#  file_handler = logging.FileHandler(simple_logging_file)
#
#  ## Setup handlerformatting
#  stream_handler.setFormatter(simple_logging_formatting)
#  file_handler.setFormatter(simple_logging_formatting)
#
#  ## Setup handler levels
#  stream_handler.setLevel(simple_logging_level)
#  file_handler.setLevel(simple_logging_level)
#
#  ## Add handlers and logger level
#  logger.addHandler(stream_handler)
#  logger.addHandler(file_handler)
#  logger.setLevel(simple_logging_level)
#
#  return logger


# Just used for testing logger
def testLogger():
  logger.debug('debug test')
  logger.info('info test')
  logger.warning('warning test')
  logger.error('error test')
  logger.fatal('fatal test')
  

def setupLogger():
  
  ##
  # TODO: make use of stream nicknames, once chicken/egg works
  ##

  # Required to pop existing handlers
  global logger

  logging_config_template = {
    'enabled': False,
    'core': {
      'enabled': False,
      'streams': []
    }
  }

  if not 'logging' in configuration.keys():
    print("??? - configuration['logging'] isn't present? -- trying fix")
    configuration['logging'] = logging_config_template
  try:
    if not 'enabled' in configuration['logging'].keys():
      logger.warning('configuration:logging:enabled is missing -- trying fix')
      configuration['logging'] = logging_config_template
  except AttributeError as error:
    logger.error('something is wrong with logging configuration -- trying fix')
    configuration['logging'] = logging_config_template
  if configuration['logging']['enabled']:

    logger = logging.getLogger()
    # TODO: double check root logger level value
    logger.setLevel('DEBUG')
    
    ##
    # TODO: attempt to iterate unknown 'logging' options as streams
    ##

    # Handle core streams
    if configuration['logging']['core']['enabled']:

      ### Configuring stream handlers
      #   Stream handlers are configured in a simple series:
      #     1)  instantiate handler
      #       a)  if stream handler, use logging StreamHandler, must also
      #           use getattr(sys.<out>), ie getattr(sys.stdout)
      #       b)  if file handler, use logging FileHandler with filepath
      #     2)  set handler formatting
      #       *)  if no formatting is being applied, value should be an
      #           empty string
      #     3)  set handler level
      #       *)  logging levels correspond to numbers, use built-in method
      #           for converting strings to corresponding number
      #     4)  attach handler to logger
      #
      #     1)  Core streams are configured (if enabled)
      #     2)  Custom/other streams are configured (if enabled)
      #       *)  custom strings are toggled globally and individually,
      #           no custom streams will run if globally disabled
      ###
      ### Setup core stdout stream
      core_stream_handler = logging.StreamHandler(getattr(sys, 'stdout'))
      core_stream_handler.setFormatter('')
      core_stream_handler.setLevel(logging.getLevelName('WARN'))
      logger.addHandler(core_stream_handler)
      ### Setup core file stream
      core_file_handler = logging.FileHandler('ansible_api.log')
      core_file_handler.setFormatter('')
      core_file_handler.setLevel(logging.getLevelName('INFO'))
      logger.addHandler(core_file_handler)

    # Handle custom/other streams
    if configuration['logging']['custom']['enabled']:
      for stream in configuration['custom']['streams']:
        if stream['enabled']:
          if stream['output'] == 'stdout' or stream['output'] == 'stderr':
            stream_handler = logging.StreamHandler(getattr(sys, stream['output']))
          else:
            stream_handler = logging.FileHandler(stream['output'])
          stream_handler.setFormatter(stream['formatter'])
          # TODO: catch strings passed as logger level names, and handle it
          stream_handler.setLevel('DEBUG')
          logger.addHandler(stream_handler)
      
      
    # Custom configuration streams were disabled
    else:
      pass

    # TODO: what happens if both core and custom are disabled?
    #logger.handlers.pop
    print('uh testing')
    logger.debug('one test debug')
    logger.info('one test info')
    logger.warning('one test warning')
    logger.error('one test error')
    logger.fatal('one test fatal')
    return logger

  # Logging was disabled
  else:

    ###
    # TODO: return a custom(?) neutered logging object or something
    ###
    print('??? - was logging really disabled?')
    return None


# FIXME: deprecated -- remove -- do not use
#def setupAdvancedLogger():
#  logger = logging.getLogger()
#  for stream in configuration['logging_streams']:
#    if stream['enabled']:
# 
#      ## Sanity-check vars
#      # output_path
#      output_path = stream['output_path']
#      if output_path is None:
#        output_path = 'stdout'
#      # formatting
#      formatting = stream['formatting']
#      if formatting is None:
#        formatting = ''
#      # level
#      level = stream['level']
#      if level is None:
#        level = 'DEBUG'
#      if isinstance(level, str):
#        level = logging.getLevelName(level.upper())
# 
#      # Set output path
#      if output_path == 'stdout':
#        handler = logging.StreamHandler(getattr(sys, output_path))
#      else:
#        handler = logging.FileHandler(output_path)
#
#      # Set formatting
#      handler.setFormatter(logging.Formatter(formatting))
#
#      # Set level
#      handler.setLevel(level)
#
#      # Add handler to logger
#      logger.addHandler(handler)
#
#  # Apply root logger level and return logger object
#  logger.setLevel(configuration['logger_root_level'])
#  return logger



# Generate a temporary token, if one is not provided
def generateAuthenticationToken():
  import binascii
  authentication_token = binascii.hexlify(os.urandom(24))
  return authentication_token.decode('utf-8')


# Read YAML file
def readYAML(filepath):
  import yaml
  print('Trying to load YAML: {}'.format(filepath))
  try:
    with open(filepath, 'r') as f:
      data = yaml.safe_load(f)
  #TODO: log the error
  except FileNotFoundError as error:
    print('file not found: {}'.format(error))
    data = {}
  except Exception as error:
    print('Error occured loading file: {}'.format(filepath))
    print('Error: {}'.format(error))
  if not data:
    print("??? Got to line {} but data wasn't defined".format(sys._getframe().f_lineno))
    data = {}
  return data


# Parse application configuration
def parseConfiguration():

  ordered_configuration_references = [
    # Core configuration which should be static
    CORE_CONFIGURATION_FILE_PATH,
    # Default configuration which should be relatively static
    DEFAULT_CONFIGURATION_FILE_PATH,
    # Local configuration which may be changed per environment
    LOCAL_CONFIGURATION_FILE_PATH
  ]
  # TODO: experiment with using a constructor here
  configuration = {}
  print('trying to merge configs')
  for configuration_reference in ordered_configuration_references:
    print('--- NEW LOOP ---')
    print('config: {}'.format(configuration))
    configuration_reference = readYAML(configuration_reference)
    print('trying config ref: {}'.format(configuration_reference))
    #configuration = {**configuration, **readYAML(configuration_reference)}
    #configuration = recursivelyMergeDictionaries(configuration, readYAML(configuration_reference))
    #configuration = recursivelyMergeDictionaries(configuration, configuration_reference)
    configuration = recursivelyMerge(configuration, configuration_reference)
  print('final config: {}'.format(configuration))
  return configuration


# FIXME: deprecated -- remove -- do not use
# Read configuration file
#def readConfigurationFile():
#  import yaml
#  with open(CONFIGURATION_FILE_PATH, 'r') as f:
#    configuration_data = yaml.safe_load(f)
#    f.close
#  return configuration_data


def reconcileConfigurationSources(*args):
  configuration = {}
  for arg in args:
    configuration = {**configuration, **arg}
  return configuration



# FIXME: I don't work!
def recursivelyMergeDictionaries(*args):
  print('args: {}'.format(*args))
  merged_dictionary = {}
  for dictionary in args:
    for key, value in dictionary.items():
      print('trying key, value: {}, {}'.format(key, value))
      if (key in merged_dictionary and isinstance(merged_dictionary[key], dict)
          and isinstance(dictionary[key], collections.Mapping)):
        merged_dictionary[key] = recursivelyMergeDictionaries(merged_dictionary[key], dictionary[key])
        print('key match found: {}'.format(key))
      else:
        merged_dictionary[key] = dictionary[key]
  return merged_dictionary


def recursivelyMerge(*args):
  merged_dictionary = {}
  dictionaries = args
  print('TEST - dictionaries: {}'.format(dictionaries))
  for dictionary in dictionaries:
    if not isinstance(dictionary, dict):
      print('??? - expected dictionary but got something else: {} - trying fix...'.format(dictionary))
      dictionary = {}

    for key, value in dictionary.items():
      
      if (key in merged_dictionary and
          #isinstance(value, dict)):
          (isinstance(value, dict) or
          isinstance(merged_dictionary[key], dict))):
      #if key in merged_dictionary:
      #  print('TEST - key in merged dict" {}'.format(key))
      #  if isinstance(value, dict):
        print('TEST - value is dict: {}'.format(value))
        print('TEST - match found')
        merged_dictionary[key] = recursivelyMerge(merged_dictionary[key], dictionary[key])
        #else:
        #  print('TEST - alt')
        #  merged_dictionary[key] = dictionary[key]
      else:
        merged_dictionary[key] = dictionary[key]
  print('TEST - about to return merged dict: {}'.format(merged_dictionary))
  return merged_dictionary
    
    


@app.route('/{}'.format(APP_NAME.lower().replace(' ', '_')), methods=['GET', 'POST'])
def webhook():
  if request.method == 'GET':
    authentication_token = request.args.get('authentication_token')
    #if authentication_token == AUTHENTICATION_TOKEN:
    if authentication_token == configuration['authentication_token']:
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
        #os.system('ansible-playbook {} -i {}  -l {} --extra-vars "{}"'.format(ANSIBLE_PLAYBOOK_PATH, ANSIBLE_INVENTORY_PATH, request.json['hostname'], request.json['extra_vars']))
        #os.system('ansible-playbook {} -i {}  -l {} --extra-vars "{}"'.format(configuration['ansible_playbook_path'], ANSIBLE_INVENTORY_PATH, request.json['hostname'], request.json['extra_vars']))
        os.system('ansible-playbook {} -i {}  -l {} --extra-vars "{}"'.format(configuration['ansible_playbook_path'], configuration['ansible_inventory_path'], request.json['hostname'], request.json['extra_vars']))
        return jsonify({'status':'success'}), 200
    else:
      return jsonify({'status':'not authorized'}), 401

  else:
    abort(400)

#print('test test test')
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
#_level = logging.getLevelName('DEBUG')
#logger.setLevel(_level)
#print(logger.getEffectiveLevel())
#logger.setLevel(logging.getLevelName('DEBUG'))
logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler(getattr(sys, 'stdout'))
_handler.setFormatter('')
_handler.setLevel(logging.DEBUG)
logger.addHandler(_handler)
logger.debug('test test debug')
logger.info('test test info')
logger.warning('test test warn')
logger.error('test test error')
logger.fatal('test test fatal')

# Read configuration data from file
#configuration_data = readConfigurationFile()
#print(configuration_data)

# Read core configuration data
#core_configuration_data = readYAML(CORE_CONFIGURATION_FILE_PATH)
#print(core_configuration_data)

# Reconcile multiple configuration sources
#configuration = reconcileConfigurationSources(core_configuration_data, configuration_data)
#print(configuration)
configuration = parseConfiguration()
print(configuration)

logger.info('Rebuilding logger...')
logger.handlers.pop()
logger = setupLogger() or DummyObject()
testLogger()

#if AUTHENTICATION_TOKEN is None:
#if configuration['authentication_token'] is None:
if not 'authentication_token' in configuration.keys():
  #print('{}_AUTHENTICATION_TOKEN has not been set in the environment.\nGenerating random token...'.format(APP_NAME.upper().replace(' ', '_')))
  print('Authentication token has not been set.\nGenerating random token...')
  #token = generateAuthenticationToken()
  configuration['authentication_token'] = generateAuthenticationToken()
  #print('Token: %s' % token)
  print('Token: %s' % configuration['authentication_token'])
  #AUTHENTICATION_TOKEN = token
#if ANSIBLE_PLAYBOOK_PATH is None:
#  raise Exception('ANSIBLE_PLAYBOOK_PATH is not defined!')
#if ANSIBLE_INVENTORY_PATH is None:
#  raise Exception('ANSIBLE_INVENTORY_PATH is not defined!')


if __name__ == '__main__':
    app.run()
