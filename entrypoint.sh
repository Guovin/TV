#!/bin/bash

pipenv run python /app/main.py scheduled_task

service cron start

pipenv run gunicorn -b :8000 main:app