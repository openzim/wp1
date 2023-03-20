FROM python:3.9

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
RUN mkdir app
COPY requirements.txt app/requirements.txt
RUN pip3 install --no-cache-dir -r app/requirements.txt
COPY . app

# Start
CMD supervisord -c /usr/src/app/supervisord-dev.conf -n
