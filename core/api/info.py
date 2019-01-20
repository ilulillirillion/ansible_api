#!/usr/bin/env python3


from flask import jsonify
#from .starter import app
from .blueprint import app, configuration

test_singleton_hardcoded = 'success'

@app.route('/info')
def return_info():


  info = {}
  info['hardcoded_test_variable_1'] = 1
  try:
    info = { **info, **configuration }
  except NameError:
    pass

  info = jsonify(info)

  #return info
  return jsonify(configuration)
