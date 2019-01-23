#!/usr/bin/env python3


from flask import jsonify
from flask_restful import Resource
from .blueprint import app


#@app.route('/info')
#@app.security_handler.authorization_required
#def return_info():
#  return jsonify(configuration)


class Info(Resource):

  @app.security_handler.authorization_required
  def get(self):
    return jsonify(app.configuration)


app.api.add_resource(Info, '/info')
