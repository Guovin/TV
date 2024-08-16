#!/bin/bash

for file in /tv_config/*; do
  filename=$(basename "$file")
  target_file="$APP_WORKDIR/config/$filename"
  if [ ! -e "$target_file" ]; then
    cp "$file" "$target_file"
  fi
done

pipenv run python $APP_WORKDIR/main.py