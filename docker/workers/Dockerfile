FROM python:3.14.4

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app

RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir pipenv
WORKDIR /usr/src/app
RUN pipenv install --system --deploy --ignore-pipfile

# Recurring jobs (formerly system cron) are scheduled by the `rq cron`
# supervisord program; see cron_config.py.

# Start
CMD supervisord -c /usr/src/app/supervisord.conf -n
