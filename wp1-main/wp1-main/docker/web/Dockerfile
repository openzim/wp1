FROM python:3.12

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
COPY . app

RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir pipenv
WORKDIR /usr/src/app
RUN pipenv install --system --deploy --ignore-pipfile

# Start
COPY docker/web/start.sh /usr/local/bin/start.sh
CMD start.sh
