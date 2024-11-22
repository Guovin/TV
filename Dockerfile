FROM python:3.13 AS builder

ARG APP_WORKDIR=/gtv
ARG LITE=false

ENV APP_WORKDIR=$APP_WORKDIR

WORKDIR $APP_WORKDIR

COPY . $APP_WORKDIR

RUN pip install -i https://mirrors.aliyun.com/pypi/simple pipenv \
  && if [ "$LITE" = true ]; then pipenv install; else pipenv install && pipenv install selenium; fi

FROM python:3.13-slim

ARG APP_WORKDIR=/gtv
ARG LITE=false

ENV APP_WORKDIR=$APP_WORKDIR

WORKDIR $APP_WORKDIR

COPY --from=builder $APP_WORKDIR $APP_WORKDIR

RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n \
  deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware\n \
  deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware\n" \
  > /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends cron \
  && if [ "$LITE" = false ]; then apt-get install -y --no-install-recommends chromium chromium-driver; fi \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN (crontab -l ; \
  echo "0 22 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task"; \
  echo "0 10 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task") | crontab -

EXPOSE 8000

COPY entrypoint.sh /gtv_entrypoint.sh

RUN chmod +x /gtv_entrypoint.sh

ENTRYPOINT ["/gtv_entrypoint.sh"]