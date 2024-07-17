#!/bin/bash

pipenv run python $APP_WORKDIR/main.py scheduled_task

service cron start