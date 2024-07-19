FROM python:3.8-slim

ARG APP_WORKDIR=/tv

ENV APP_WORKDIR=$APP_WORKDIR

COPY . $APP_WORKDIR

WORKDIR $APP_WORKDIR

RUN pip install -i https://mirrors.aliyun.com/pypi/simple pipenv

RUN pipenv install

RUN sed -i "s@deb.debian.org@mirrors.aliyun.com@g" /etc/apt/sources.list \
  && sed -i "s@security.debian.org@mirrors.aliyun.com@g" /etc/apt/sources.list

RUN apt-get update && apt-get install -y cron

ARG INSTALL_CHROMIUM=false

RUN if [ "$INSTALL_CHROMIUM" = "true" ]; then apt-get install -y chromium chromium-driver cron; fi

RUN (crontab -l ; echo "0 22 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task 2>&1 | tee -a /var/log/tv.log"; echo "0 10 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task 2>&1 | tee -a /var/log/tv.log") | crontab -

EXPOSE 8000

COPY entrypoint.sh /tv_entrypoint.sh

RUN chmod +x /tv_entrypoint.sh

ENTRYPOINT /tv_entrypoint.sh