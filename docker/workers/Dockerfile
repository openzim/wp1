FROM python:3.7

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY lucky app
RUN apt-get update && apt-get install -y --no-install-recommends cron
RUN pip3 install -r app/requirements.txt

# Start
COPY docker/workers/start.sh /usr/local/bin/start.sh
CMD start.sh
