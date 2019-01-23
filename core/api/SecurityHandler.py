#!/usr/bin/env python3


from flask import jsonify, request
from datetime import datetime, timedelta
from functools import wraps


class SecurityHandler():
  authorized_clients = {}

  @staticmethod
  def authorize_client(client_address):
    print('authorizing client...')
    SecurityHandler.authorized_clients[client_address] = datetime.now()

  @staticmethod
  def consider_authentication(request):
    print(f'evaluating authentication...')
    if 'security_token' in request.args:
      token = request.args.get('security_token')
      if token == SecurityHandler.token:
        SecurityHandler.authorize_client(request.remote_addr)
        return SecurityHandler.is_authorized(request)
    else:
      print('no security token passed')
      return False

  @staticmethod
  def is_authorized(request):
    print('checking authorization...')
    print('request: <{request}>')
    client = request.remote_addr
    if client in SecurityHandler.authorized_clients:
      if datetime.now() - SecurityHandler.authorized_clients.get(client) < timedelta(hours=SecurityHandler.client_timeout_hours):
        SecurityHandler.authorize_client(client)
        return True
      else:
        return SecurityHandler.consider_authentication(request)
    else:
      return SecurityHandler.consider_authentication(request)

  @staticmethod
  def authorization_required(wrapped_function):
    @wraps(wrapped_function)
    def wrap(*args, **kwargs):
      if SecurityHandler.is_authorized(request):
        return wrapped_function(*args, **kwargs)
      else:
        #print(f"redirecting since <{request.remote_addr}> wasn't authenticated.")
        print("redirecting since <{}> wasn't authenticated.".format(request.remote_addr))
        return jsonify({'status':'redirected'})
    return wrap
