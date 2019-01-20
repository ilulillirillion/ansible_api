#!/usr/bin/env python


from flask import jsonify, request
from .starter import app


@app.route('/authorize_client')
def authorize_client():
  security_token = request.args.get('security_token')
  if security_token == 'PLACEHOLDER_REMOVE':
    return jsonify({'status':'test token success'}), 200
  else:
    return jsonify({'status':'test token authentication failure'}), 401
