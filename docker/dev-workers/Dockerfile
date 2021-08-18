FROM python:3.9

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app
RUN apt-get update && \
  apt-get install -y --no-install-recommends cron && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3059
RUN pip3 install --no-cache-dir -r app/requirements.txt

# Start
CMD supervisord -c /usr/src/app/supervisord-dev.conf -n
