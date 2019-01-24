#!/usr/bin/env python3


from flask import jsonify
from flask_restful import Resource
from .blueprint import app


class UserTest(Resource):
  
  @app.security_handler.authorization_required
  def get(self, username):
    return jsonify({'username':username})


app.api.add_resource(UserTest, '/user/<username>')
