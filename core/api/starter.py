#!/usr/bin/env python3


from flask import Flask, jsonify, redirect
from .configuration import configuration
from .SecurityHandler import SecurityHandler


app = Flask(__name__)
app.security_handler = SecurityHandler
app.security_handler.token = configuration['security_token']
if 'client_timeout_hours' in configuration:
  app.security_handler.client_timeout_hours = configuration['client_timeout_hours']
else:
  app.security_handler.client_timeout_hours = 24


@app.route('/is_running')
@app.security_handler.authorization_required
def check_if_running():
  print(f'test test')
  return jsonify({'status':'running'}), 200
