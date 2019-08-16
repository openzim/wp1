FROM python:3.7

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install -r app/requirements.txt

# Schedule tasks through cron
RUN echo "0 0 * * * * /usr/bin/flock -n /run/lock/enqueue-all.cron.lock    -c 'python /usr/src/app/enqueue-all.py    > /dev/shm/enqueue-all.cron.log    2>&1'" > /etc/cron.d/enqueue-all
RUN echo "0 4 * * * * /usr/bin/flock -n /run/lock/enqueue-global.cron.lock -c 'python /usr/src/app/enqueue-global.py > /dev/shm/enqueue-global.cron.log 2>&1'" > /etc/cron.d/enqueue-global

# Start
CMD cron && supervisord -c /usr/src/app/supervisord.conf -n
