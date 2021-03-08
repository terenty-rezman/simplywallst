#!/usr/bin/env bash

# terminate script on error
set -e

source venv/bin/activate
export FLASK_APP=server.py
flask run