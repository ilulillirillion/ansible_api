#!/usr/bin/env python3


# Initialize configuration for the application
from .configuration import configuration

# Initialize the app itself, add 'is_running' endpoint
from .starter import app

# Testing purposes only, adds a test endpoint
from .test import app

# Add 'authorized_client' endpoint to app
from .authorize_client import app

# Add 'info' endpoint to app
from .info import app
