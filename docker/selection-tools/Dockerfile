FROM python:3.14

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    cron openssh-client ca-certificates util-linux p7zip-full unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

VOLUME /data

WORKDIR /app

RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock .

RUN pipenv install --system --deploy --ignore-pipfile

COPY . .

ENV PYTHONPATH=/app


RUN mkdir -p /etc/cron.monthly && \
    echo "#!/bin/sh" > /etc/cron.monthly/wp1_selection_tools && \
    echo "/usr/bin/flock -w 0 /dev/shm/cron.lock python -m wp1.selection_tools.entrypoint build-all --data-dir /data" >> /etc/cron.monthly/wp1_selection_tools && \
    chmod a+x /etc/cron.monthly/wp1_selection_tools

CMD ["cron", "-f"]
