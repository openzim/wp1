FROM python:3.12.0

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir pipenv
WORKDIR /usr/src/app
RUN pipenv install --system --deploy --ignore-pipfile

RUN chmod -R a+x /usr/src/app/cron/

# Schedule tasks through cron
# Currently disabled: https://github.com/openzim/wp1/issues/875
# RUN echo "0 0 * * * root /usr/src/app/cron/enqueue-all.sh > /var/log/wp1bot/enqueue-all.cron.log 2>&1" > /etc/cron.d/enqueue-all
# RUN echo "0 4 * * * root /usr/src/app/cron/update-global-articles.sh > /var/log/wp1bot/update-global-articles.cron.log 2>&1" > /etc/cron.d/update-global-articles
# RUN echo "0 5 * * * root /usr/src/app/cron/enqueue-global.sh > /var/log/wp1bot/enqueue-global.cron.log 2>&1" > /etc/cron.d/enqueue-global

# Start
CMD cron && supervisord -c /usr/src/app/supervisord.conf -n
