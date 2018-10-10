#!/bin/bash

exec gunicorn --config operations_api/gunicorn.py operations_api.wsgi
