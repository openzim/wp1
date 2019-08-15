FROM python:3.7

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app
RUN pip3 install -r app/requirements.txt

# Start
COPY docker/web/start.sh /usr/local/bin/start.sh
CMD start.sh
