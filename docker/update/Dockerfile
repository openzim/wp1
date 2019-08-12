FROM python:3.7

LABEL maintainer="kiwix"

WORKDIR /usr/src

COPY lucky app

RUN apt-get update && apt-get install -y --no-install-recommends cron

RUN pip3 install -r app/requirements.txt

ENTRYPOINT ["python", "app/update.py"]
