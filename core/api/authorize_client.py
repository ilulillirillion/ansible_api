#!/usr/bin/env python


from flask import jsonify, request
from .blueprint import app, configuration


@app.route('/authorize_client')
def authorize_client():
  security_token = request.args.get('security_token')
  if security_token == configuration['security_token']:
    app.security_handler.whitelist_client(request.remote_addr)
    return jsonify({'status':'test token success'}), 200
  else:
    return jsonify({'status':'test token authentication failure'}), 401
