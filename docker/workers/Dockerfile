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
CMD echo "0 0  * * * root /usr/bin/flock -w 0 /dev/shm/enqueue-all.cron.lock    python /usr/src/app/enqueue-all.py    > /dev/shm/enqueue-all.cron.log    2>&1" > /etc/cron.d/enqueue-all
CMD echo "0 23 * * * root /usr/bin/flock -w 0 /dev/shm/enqueue-global.cron.lock python /usr/src/app/enqueue-global.py > /dev/shm/enqueue-global.cron.log 2>&1" > /etc/cron.d/enqueue-global

# Start
COPY docker/workers/start.sh /usr/local/bin/start.sh
CMD start.sh
