FROM python:3.8-slim

ARG APP_WORKDIR=/tv

ENV APP_WORKDIR=$APP_WORKDIR

COPY . $APP_WORKDIR

WORKDIR $APP_WORKDIR

RUN pip install -i https://mirrors.aliyun.com/pypi/simple pipenv

RUN pipenv install

RUN echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n \
  deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n \
  deb https://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.ustc.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware\n \
  deb https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware\n \
  deb-src https://mirrors.ustc.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware\n" \
  > /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
  cron \
  wget \
  xz-utils

RUN wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz && \
  tar -xf ffmpeg-release-i686-static.tar.xz && \
  mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
  mv ffmpeg-*-static/ffprobe /usr/local/bin/ && \
  rm -rf ffmpeg-*-static*

ARG INSTALL_CHROMIUM=false

RUN if [ "$INSTALL_CHROMIUM" = "true" ]; then \
  apt-get install -y --no-install-recommends \
  chromium \
  chromium-driver; \
  fi

RUN  apt-get clean && rm -rf /var/lib/apt/lists/*

RUN (crontab -l ; echo "0 22 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task 2>&1 | tee -a /var/log/tv.log"; echo "0 10 * * * cd $APP_WORKDIR && /usr/local/bin/pipenv run python main.py scheduled_task 2>&1 | tee -a /var/log/tv.log") | crontab -

EXPOSE 8000

COPY entrypoint.sh /tv_entrypoint.sh

RUN chmod +x /tv_entrypoint.sh

ENTRYPOINT /tv_entrypoint.sh