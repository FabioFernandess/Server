#!/bin/sh
export FLASK_APP=./server/index.py
source $(pipenv --venv)/bin/activate
service postgresql start
flask run -h 0.0.0.0