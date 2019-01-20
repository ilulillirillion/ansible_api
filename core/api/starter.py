#!/usr/bin/env python3


from flask import Flask, jsonify


app = Flask(__name__)


@app.route('/is_running')
def check_if_running():
  return jsonify({'status':'running'}), 200
