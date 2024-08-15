#!/bin/bash

for file in /tv_config/*; do
  filename=$(basename "$file")
  target_file="$APP_WORKDIR/config/$filename"
  if [ ! -e "$target_file" ]; then
    cp "$file" "$target_file"
  fi
done

PYTHONUNBUFFERED=1 pipenv run python $APP_WORKDIR/main.py scheduled_task 2>&1 | tee -a /var/log/tv.log

cron

tail -f /var/log/tv.log