#!/usr/bin/env python3


import sys
#import yaml
import re
import os
#import ruamel.yaml as yaml


from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()
dummy_data = {
  'test': 'test_value'
}

class VaultVar:
  yaml_tag = '!vault'

  def __init__(self):
    self.name = 'testname'
    self.age = 'testage'

  @classmethod
  def to_yaml(cls, representer, data):
    print(f'cls: {cls}')
    print(f'representer: {representer}')
    #print(f'data: {data}')
    #return representer.represent_scalar(cls.yaml_tag, data)
    return representer.represent_scalar(cls.yaml_tag, dummy_data)
    #return representer.represent_mapping(cls.yaml_tag, dummy_data)
    #return representer.represent_scalar(data)

  #def to_yaml(cls, representer, data):
  #  if hasattr(data, '__getstate__'):
  #    state = data.__getstate__()
  #  else:
  #    state = data.__dict__.copy()
  #  return self.represent_mapping(tag, state, flow_style=flow_style)

  @classmethod
  def from_yaml(cls, constructor, node):
    data = CommentedMap()
    #constructor.construct_mapping(node, data, deep=True)
    constructor.construct_scalar(node)
    return cls(**data)

  def __str__(self):
    return f'vault({data})'


#def yaml_hell():
yaml.register_class(VaultVar)


#class VaultTag(yaml.YAMLObject):
#  yaml_tag = u'!vault'

#  def __init__(self, value):
#    self.value = value  

#  def __repr__(self:
#    return value

#  @staticmethod
#  def yaml_constructor(loader, node):
#    return VaultTag(loader.constr


#def Custom_Constructor(loader, tag_suffix, node):
#  print(loader)
#  print(tag_suffix)
#  print(node)
#  return tag_suffix + ' ' + node.value

#yaml.add_multi_constructor('!', Custom_Constructor)


#class VaultTag(yaml.YAMLObject):
#  yaml_tag = u'!vault'
  
#  def __init__(self, vault_var):
#    self.vault_var = vault_var

#  @classmethod
#  def from_yaml(cls, loader, node):
#    return VaultTag(node.value)

#  @classmethod
#  def to_yaml(cls, dumper, data):
#    return dumper.represent_scalar(cls.yaml_tag, data.env_var)

#class V2SafeLoader(yaml.SafeLoader):
#  def let_v2_through(self, node):
#    node.value = '!vault |\n' + node.value
    #node.value = node.value.strip('\n')
    #node.tag = 'tag:yaml.org,2002:str'
    #print(node)
    #print(node.value)
#    return self.construct_scalar(node)
#    #return node.value


def generic_constructor(loader, node):
  node.tag = 'tag:yaml.org,2002:value'
  node.value = '!vault |\n' + node.value
  print(node)
  for line in node.value.splitlines():
    print(f'test--{line}')
  return node.value


#yaml.SafeLoader.add_constructor('!vault', generic_constructor)


#class V2SafeDumper



#yaml.SafeLoader.add_constructor('!vault', yaml.SafeLoader.construct_scalar)
#V2SafeLoader.add_constructor('!vault', V2SafeLoader.let_v2_through)

#yaml.SafeLoader.add_constructor('!vault', yaml.SafeLoader.construct_scalar)



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
  #group_definitions = yaml.load(group_definitions_file, Loader=V2SafeLoader)
  #group_definitions = yaml.safe_load(group_definitions_file)
  group_definitions = yaml.load(group_definitions_file)
  #group_definitions = yaml.load()
  #group_definitions = yaml.safe_load(group_definitions_file)
  group_definitions_file.close


group_variables_files = []
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
      group_variables_files.append(group_variables_file)
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
      print(f"test group defs: <{group_definition['vars']}>")
      with open(group_variables_file, 'w+') as f:
        #yaml.safe_dump(group_definition['vars'], f, default_flow_style=False)
        yaml.dump(group_definition['vars'], f)
        

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


variable_values_cleaned = 0
def cleanup_variable_value(variable_value):
  global variable_values_cleaned

  print(f'Cleaning variable <{variable_value}> (<{type(variable_value)}>)')
  if '__iter__' in variable_value:
    print(f'<{variable_value}> appears iterable')
  if isinstance(variable_value, list):
    print('recursing variable cleanup on list')
    for single_value in variable_value:
      cleanup_variable_value(single_value)
  if isinstance(variable_value, dict):
    #print(f'<{variable_value}> is a dictionary')
    #cleanup_variable_value(variable_value)
    print('recursing variable cleanup on dictionary')
    for key, value in variable_value.items():
      cleanup_variable_value(value)
  variable_values_cleaned += 1
  #print(f'variables_cleaned: <{variable_values_cleaned}>')

  # Fix vault strings with double spaces
  if isinstance(variable_value, str) and '!vault' in variable_value:
    print('VAULT FOUND')


def cleanup_group_variables_files(variables_files):
  for variables_file in variables_files:
    print(f'Cleaning up <{variables_file}>')
    with open(variables_file, 'r') as f:
      #variables_data = yaml.safe_load(f)
      variables_data = yaml.load(f)
    #print(f'variables data: <{variables_data}>')
    #for variable_data in variables_data:
    #  cleanup_variable_data(variable_data)
    for key, value in variables_data.items():
      #print(f'Attempting cleanup on <{key}>, <{value}>')
      cleanup_variable_value(value)


#def cleanup_variables_files(variables_files):
#  for variables_file in variables_files:
#    print(f'Cleaning up <{variables_files}>'
#    with open(variables_files, 'r'
    


cleanup_group_variables_files(group_variables_files)
