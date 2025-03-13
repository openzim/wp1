FROM python:3.12

# Meta
LABEL maintainer="kiwix"

# Python app
WORKDIR /usr/src
RUN mkdir app
RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir pipenv
COPY ./Pipfile app/Pipfile
COPY ./Pipfile.lock app/Pipfile.lock
WORKDIR /usr/src/app
RUN pipenv install --system --deploy --ignore-pipfile
COPY . ../app

# Start
CMD supervisord -c /usr/src/app/supervisord-dev.conf -n
