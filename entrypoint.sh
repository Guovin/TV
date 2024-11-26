#!/bin/bash

for file in /iptv_config/*; do
  filename=$(basename "$file")
  target_file="$APP_WORKDIR/config/$filename"
  if [ ! -e "$target_file" ]; then
    cp -r "$file" "$target_file"
  fi
done

. /.venv/bin/activate

service cron start

python $APP_WORKDIR/main.py

gunicorn -w 4 -b 0.0.0.0:8000 main:app