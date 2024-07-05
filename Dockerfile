FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install -i https://mirrors.aliyun.com/pypi/simple pipenv

RUN pipenv install

RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list \
  && sed -i 's@security.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y chromium chromium-driver cron

RUN (crontab -l 2>/dev/null; echo "0 0 * * * cd /app && pipenv run python main.py scheduled_task") | crontab -

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]