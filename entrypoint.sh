#!/bin/bash

service cron start

pipenv run python $APP_WORKDIR/main.py

gunicorn -w 4 -b 0.0.0.0:8000 main:app