#!/usr/bin/env python3


#from flask import Flask, jsonify
from flask import jsonify
from .starter import app

#app = Flask(__name__)


@app.route('/test')
def test():
  return jsonify({'status':'test return'}), 200
