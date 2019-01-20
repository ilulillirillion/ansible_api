#!/usr/bin/env bash

echo 'Tesing Flask API...'
curl 127.0.0.1:5000/is_running;
curl 127.0.0.1:5000/test;
curl 127.0.0.1:5000/authorize_client;
curl 127.0.0.1:5000/info;
echo 'Test complete'
