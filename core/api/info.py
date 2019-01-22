#!/usr/bin/env python3


from flask import jsonify
from .blueprint import app, configuration


@app.route('/info')
@app.security_handler.authorization_required
def return_info():
  return jsonify(configuration)
