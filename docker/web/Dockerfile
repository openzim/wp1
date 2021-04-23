FROM python:3.9

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app
RUN pip3 install --no-cache-dir -r app/requirements.txt

# Start
COPY docker/web/start.sh /usr/local/bin/start.sh
CMD start.sh
