#!/usr/bin/env python3


import yaml
import os


#configuration = {}
#inline_configuration['configuration_test_variable_1'] = 1
configuration_filepaths = [
  'default/config.yaml',
  'local/config.yaml'
]


def read_yaml(filepath):
  if not os.path.exists(filepath):
    print(f'attempted to read non-existent file <{filepath}>!')
  else:
    with open(filepath, 'r') as f:
      yaml_contents = yaml.safe_load(f)
    return yaml_contents


def merge_recursively(*args):

  print(f'args: <{args}>')

  #if isinstance(*args, list):
  #  print(f'args is a list')
      
  print(f'Instantiating empty merged_data')
  merged_data = {}

  for data_source in args:
    print(f'Processing data_source: <{data_source}>')
    if not isinstance(data_source, dict):
      print(f"expected <{data_source}> to be a dictionary but it's not!")
      data_source = {}

    print(f'About to iterate data source')
    for key, value in data_source.items():
      print(f'Considering <{key}> for recursive merge')
      if (key in merged_data and
          (isinstance(value, dict) or
          isinstance(merged_data[key], dict))):
        print(f'Recursively merging <{key}>')
        merged_data[key] = recursive_merge(merged_data[key], data_source[key])
      else:
        print(f'Overwriting key <{key}>')
        merged_data[key] = data_source[key]

  print(f'Returning merged data: <{merged_data}>')
  return merged_data


def merge_configuration_data(data_sources):
  inline_configuration = {'inline_test_variable': 1}
  configuration_data = []
  configuration_data.append(inline_configuration)
  for data_source in data_sources:
    print(f'parsing configuration source <{data_source}>')
    #configuration_data = read_yaml(data_source)
    data = read_yaml(data_source)
    configuration_data.append(data)
  print(f'Configuration data: <{configuration_data}>')
  #print(f'Configuration (pre-merge): <{configuration}>')
  configuration = merge_recursively(configuration_data)
  #print(f'Configuration data (post-merge): <{configuration}>')
  return configuration


def parse_configuration(configuration_sources):
  #configuration = merge_configuration_data(configuration_sources)

  configuration = {}
  for configuration_source in configuration_sources:

    # Check if it's a filepath
    if True:
      configuration_data = read_yaml(configuration_source)
      configuration = merge_recursively(configuration, configuration_data)

    else:
      print(f'only supports filepaths for now')
      return None

  return configuration


configuration = parse_configuration(configuration_filepaths)
print(f'Final configuration: <{configuration}>')
