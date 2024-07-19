#!/bin/bash

pipenv run python $APP_WORKDIR/main.py scheduled_task 2>&1 | tee -a /var/log/tv.log

cron

tail -f /var/log/tv.log