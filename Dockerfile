FROM python:3.10.8-bullseye

# Upgrade and install dependencies
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update &&  \
    apt-get -y upgrade &&  \
    apt-get -y install libpq-dev gcc curl cron

ENV PYTHONFAULTHANDLER=1  \
  PYTHONUNBUFFERED=true  \
  PYTHONHASHSEED=random  \
  PYTHONDONTWRITEBYTECODE=1
  # pip:
  # PIP_NO_CACHE_DIR=off  \
  # PIP_DEFAULT_TIMEOUT=100

RUN mkdir /usr/app
WORKDIR /usr/app

# Installing requirements
COPY requirements.txt ./
# RUN pip install --no-cache-dir -r /usr/app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
        pip install -r /usr/app/requirements.txt

COPY . .

# About crontab
ADD crontab /etc/cron.d/crawler-cron-file
RUN chmod 0644 /etc/cron.d/crawler-cron-file
RUN crontab /etc/cron.d/crawler-cron-file
