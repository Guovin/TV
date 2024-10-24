FROM python:3.8-slim-buster AS builder

COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple pipenv \
  && pipenv install --system

FROM python:3.8-slim-buster

ARG APP_WORKDIR=/tv

ENV APP_WORKDIR=$APP_WORKDIR \
  PYTHONUNBUFFERED=1

WORKDIR $APP_WORKDIR

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

ENV PYTHONPATH /usr/local/lib/python3.8/site-packages

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

ARG INSTALL_CHROMIUM=false

RUN if [ "$INSTALL_CHROMIUM" = "true" ]; then \
  apt-get install -y --no-install-recommends \
  chromium \
  chromium-driver; \
  fi

RUN apt-get update && apt-get install -y --no-install-recommends \
  cron \
  ffmpeg \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN (crontab -l ; \
  echo "0 22 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task"; \
  echo "0 10 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task") | crontab -

COPY . $APP_WORKDIR

COPY entrypoint.sh /tv_entrypoint.sh

COPY config /tv_config

RUN chmod +x /tv_entrypoint.sh

ENTRYPOINT /tv_entrypoint.sh

EXPOSE 8000