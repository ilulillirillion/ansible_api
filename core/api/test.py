#!/usr/bin/env python3


#from flask import Flask, jsonify
from flask import jsonify
#from .starter import app
from .blueprint import app, configuration

#app = Flask(__name__)


@app.route('/test')
def test():
  return jsonify({'status':'test return'}), 200
