FROM python:3.13 AS builder

ARG LITE=False

WORKDIR /app

COPY Pipfile* ./

RUN pip install -i https://mirrors.aliyun.com/pypi/simple pipenv

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy\
  && if [ "$LITE" = False ]; then pipenv install selenium; fi


FROM python:3.13-slim

ARG APP_WORKDIR=/iptv-api
ARG LITE=False

ENV APP_WORKDIR=$APP_WORKDIR
ENV LITE=$LITE
ENV PATH="/.venv/bin:$PATH"

WORKDIR $APP_WORKDIR

COPY . $APP_WORKDIR

COPY --from=builder /app/.venv /.venv

RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware\n \
  deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb https://mirrors.aliyun.com/debian/ bookworm-backports main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.aliyun.com/debian/ bookworm-backports main contrib non-free non-free-firmware\n \
  deb https://mirrors.aliyun.com/debian-security/ bookworm-security main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.aliyun.com/debian-security/ bookworm-security main contrib non-free non-free-firmware\n" \
  > /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends cron

RUN if [ "$LITE" = False ]; then apt-get install -y --no-install-recommends chromium chromium-driver; fi \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN (crontab -l ; \
  echo "0 22 * * * cd $APP_WORKDIR && /.venv/bin/python main.py"; \
  echo "0 10 * * * cd $APP_WORKDIR && /.venv/bin/python main.py") | crontab -

EXPOSE 8000

COPY entrypoint.sh /iptv-api-entrypoint.sh

COPY config /iptv-api-config

RUN chmod +x /iptv-api-entrypoint.sh

ENTRYPOINT /iptv-api-entrypoint.sh